"""
Message formatting utilities for converting Slack messages to Google Chat format.

This module provides functions to parse Slack's block kit structure and
convert Slack's markdown syntax to the format expected by Google Chat.
"""

import logging
import re
from typing import Dict, List
from datetime import datetime

import emoji

# This assumes a standard logging setup. If you don't have one,
# you can replace `from slack_migrator.utils.logging import logger`
# with `import logging; logger = logging.getLogger(__name__)`
from slack_migrator.utils.logging import log_with_context, logger


def _parse_rich_text_elements(elements: List[Dict]) -> str:
    """
    Helper function to parse a list of rich text elements from Slack's block kit format.

    This function processes different types of rich text elements (text, links, emojis, user mentions)
    and applies appropriate styling (bold, italic, strikethrough) based on the element's style
    attributes.

    Args:
        elements: A list of dictionaries representing rich text elements from Slack's block kit

    Returns:
        A string with the processed rich text content including all formatting
    """

    def _apply_styles(text: str, style: dict) -> str:
        """
        Applies markdown styling to a string based on a style object.

        Takes a style dictionary containing boolean flags for different styling options
        (bold, italic, strikethrough) and applies the appropriate markdown formatting
        to the text.

        Args:
            text: The text content to style
            style: A dictionary with style flags (e.g., {'bold': True, 'italic': True})

        Returns:
            The text with markdown styling applied
        """
        if not style:
            return text

        # Apply styles in the correct order: bold -> italic -> strikethrough
        # This ensures proper nesting of markdown markers
        result = text

        if style.get("bold"):
            result = f"*{result}*"
        if style.get("italic"):
            result = f"_{result}_"
        if style.get("strike"):
            result = f"~{result}~"

        return result

    output_parts = []
    for el in elements:
        el_type = el.get("type")
        style = el.get("style", {})

        if el_type == "text":
            text_content = el.get("text", "")

            # Handle the simple cases first
            if not text_content:
                output_parts.append(text_content)
            elif not style:
                # No styling to apply - preserve text exactly
                output_parts.append(text_content)
            elif not text_content.strip():
                # Text is all whitespace - preserve exactly (no styling possible)
                output_parts.append(text_content)
            else:
                # We have both content and styling - apply styles while preserving whitespace
                # Find the span of actual content (first to last non-whitespace character)
                first_char = next(
                    i for i, c in enumerate(text_content) if not c.isspace()
                )
                last_char = next(
                    i for i, c in enumerate(reversed(text_content)) if not c.isspace()
                )
                last_char = len(text_content) - 1 - last_char

                leading_whitespace = text_content[:first_char]
                content = text_content[first_char : last_char + 1]
                trailing_whitespace = text_content[last_char + 1 :]

                styled_content = _apply_styles(content, style)
                output_parts.append(
                    f"{leading_whitespace}{styled_content}{trailing_whitespace}"
                )

        elif el_type == "link":
            url = el.get("url", "")
            text = el.get("text", url)
            # Create the base link markdown
            link_markdown = f"<{url}|{text}>"
            # Apply styles to the entire link
            output_parts.append(_apply_styles(link_markdown, style))

        elif el_type == "emoji":
            output_parts.append(f":{el.get('name', '')}:")

        elif el_type == "user":
            user_mention = f"<@{el.get('user_id', '')}>"
            # Apply styles to the user mention if any are specified
            # Note that Google Chat does not support bold or italic for user mentions
            output_parts.append(_apply_styles(user_mention, style))

    return "".join(output_parts)


def parse_slack_blocks(message: Dict) -> str:
    """
    Parse Slack block kit format from a message to extract rich text content.

    This function handles various Slack block types including sections, rich text blocks,
    headers, context blocks, and dividers. For each block type, it extracts the text content
    and applies appropriate formatting. Rich text blocks are processed recursively to handle
    nested formatting.

    Also checks for forwarded/shared message content in the attachments array.

    Supported block types:
    - section: Basic text blocks and fields
    - rich_text: Complex formatted text including sections, lists, quotes, and code blocks
    - header: Converted to bold text
    - context: Small text elements typically shown below a message
    - divider: Horizontal line separator

    Args:
        message: A dictionary containing a Slack message with 'blocks' and/or 'text' fields

    Returns:
        A string with all the formatted text content from the message blocks,
        or the raw text field if no blocks are present or no content could be extracted
    """
    # First check for forwarded message content
    forwarded_texts = []
    attachments = message.get("attachments", [])
    for attachment in attachments:
        # Check if this is a forwarded/shared message
        if attachment.get("is_share") or attachment.get("is_msg_unfurl"):
            # Try to get text from various fields in the attachment
            forwarded_text = ""
            author_info = ""
            timestamp_info = ""

            # Extract author information if available
            if attachment.get("author_name"):
                author_info = f" from {attachment['author_name']}"
            elif attachment.get("author_subname"):
                author_info = f" from {attachment['author_subname']}"

            # Extract timestamp information if available
            if attachment.get("ts"):
                # Convert timestamp to readable format
                try:
                    timestamp = float(attachment["ts"])
                    readable_time = datetime.fromtimestamp(timestamp).strftime(
                        "%B %d, %Y at %I:%M %p"
                    )
                    timestamp_info = f" (originally sent {readable_time})"
                except (ValueError, OSError):
                    # Fallback if timestamp conversion fails
                    timestamp_info = f" (originally sent at {attachment['ts']})"

            # Prefer rich message_blocks over plain text for better formatting
            if "message_blocks" in attachment:
                for msg_block in attachment.get("message_blocks", []):
                    if "message" in msg_block and "blocks" in msg_block["message"]:
                        # Recursively parse blocks from the forwarded message to preserve rich formatting
                        forwarded_text = parse_slack_blocks(msg_block["message"])
                        break

            # Fall back to plain text fields if no message_blocks available
            if not forwarded_text:
                if attachment.get("text"):
                    forwarded_text = attachment.get("text", "")
                elif attachment.get("fallback"):
                    forwarded_text = attachment.get("fallback", "")

            if forwarded_text.strip():
                # Handle bullet formatting directly for Google Chat compatibility
                lines = forwarded_text.strip().split("\n")
                improved_lines = []

                for line in lines:
                    stripped = line.strip()
                    # Handle indented bullets by converting to different bullet types
                    if re.match(r"^\s+•", line):
                        # Convert indented bullets to different bullet characters
                        indent_level = len(line) - len(line.lstrip())
                        content = (
                            stripped[1:].strip()
                            if stripped.startswith("•")
                            else stripped
                        )
                        if indent_level <= 4:
                            # Use official Google Chat bullet format for first level
                            improved_lines.append(f"* {content}")
                        elif indent_level <= 8:
                            # Calculate indentation: 4 spaces base + 5 spaces for level 1
                            indent_spaces = " " * (4 + 5)  # 9 spaces total
                            improved_lines.append(f"{indent_spaces}◦ {content}")
                        else:
                            # Calculate indentation: 4 spaces base + 5 spaces per level (assuming level 2+)
                            level = 2 if indent_level <= 12 else 3
                            indent_spaces = " " * (4 + (5 * level))
                            improved_lines.append(f"{indent_spaces}▪ {content}")
                    elif stripped.startswith("•"):
                        # Convert top-level bullets to official Google Chat format
                        content = stripped[1:].strip() if len(stripped) > 1 else ""
                        improved_lines.append(f"* {content}")
                    else:
                        improved_lines.append(line)

                forwarded_text = "\n".join(improved_lines)

                # Add indicator with author and timestamp info when available
                # Use Google Chat bold formatting (*text* instead of **text**)
                header = f"*Forwarded message{author_info}{timestamp_info}:*"
                forwarded_texts.append(f"{header}\n{forwarded_text}")

    # Now process the main message blocks
    if "blocks" not in message or not message["blocks"]:
        main_text = message.get("text", "")
        # If we have forwarded content but no main text, use forwarded content
        if not main_text.strip() and forwarded_texts:
            return "\n\n".join(forwarded_texts)
        # If we have both, combine them
        elif main_text.strip() and forwarded_texts:
            return main_text + "\n\n" + "\n\n".join(forwarded_texts)
        # Otherwise just return main text
        else:
            return main_text

    texts = []
    blocks_data = message.get("blocks", [])

    for block in blocks_data:
        block_type = block.get("type")

        if block_type == "section":
            if text_obj := block.get("text"):
                texts.append(text_obj.get("text", ""))
            for field in block.get("fields", []):
                if field and isinstance(field, dict):
                    texts.append(field.get("text", ""))

        elif block_type == "rich_text":
            # Process rich text elements, handling lists specially to maintain proper indentation
            rich_text_parts = []
            list_items = []  # Track consecutive list items

            for element in block.get("elements", []):
                element_type = element.get("type")

                if element_type == "rich_text_section":
                    # If we have accumulated list items, add them first
                    if list_items:
                        rich_text_parts.append("\n".join(list_items))
                        list_items = []

                    rich_text_content = _parse_rich_text_elements(
                        element.get("elements", [])
                    )
                    if rich_text_content.strip():  # Only add non-empty content
                        # Remove excessive trailing newlines but preserve intentional line breaks
                        cleaned_content = rich_text_content.rstrip("\n")
                        if (
                            cleaned_content
                        ):  # Make sure we still have content after cleaning
                            rich_text_parts.append(cleaned_content)

                elif element_type == "rich_text_list":
                    # Process list item with Google Chat compatible formatting
                    list_style = element.get("style", "bullet")
                    indent_level = element.get("indent", 0)

                    # Use proper Google Chat list formatting for first level
                    # and fallback characters for deeper levels
                    if list_style == "bullet":
                        if indent_level == 0:
                            # Use official Google Chat bullet format for proper line wrapping
                            prefix = "*"  # Official Google Chat bullet format
                        elif indent_level == 1:
                            prefix = "◦"  # Hollow bullet for level 1
                        else:
                            prefix = "▪"  # Small bullet for level 2+
                    else:
                        # For numbered lists
                        pass  # Will use i+1 in the loop

                    for i, item in enumerate(element.get("elements", [])):
                        item_text = _parse_rich_text_elements(item.get("elements", []))
                        if list_style == "bullet":
                            if indent_level == 0:
                                # Format first-level bullets with official Google Chat format
                                list_items.append(f"* {item_text}")
                            else:
                                # Calculate indentation: 4 spaces base + 5 spaces per level
                                indent_spaces = " " * (4 + (5 * indent_level))
                                list_items.append(
                                    f"{indent_spaces}{prefix} {item_text}"
                                )
                        else:
                            # For numbered lists
                            if indent_level == 0:
                                list_items.append(f"{i + 1}. {item_text}")
                            else:
                                # Same indentation formula for numbered lists
                                indent_spaces = " " * (4 + (5 * indent_level))
                                list_items.append(
                                    f"{indent_spaces}{i + 1}. {item_text}"
                                )

                elif element_type == "rich_text_quote":
                    # If we have accumulated list items, add them first
                    if list_items:
                        rich_text_parts.append("\n".join(list_items))
                        list_items = []

                    quote_content = _parse_rich_text_elements(
                        element.get("elements", [])
                    )
                    # Split by paragraph, wrap each in italics, and rejoin.
                    paragraphs = quote_content.strip().split("\n\n")
                    italicized_paragraphs = [
                        f"_{p.strip()}_" for p in paragraphs if p.strip()
                    ]
                    rich_text_parts.append("\n\n".join(italicized_paragraphs))

                elif element_type == "rich_text_preformatted":
                    # If we have accumulated list items, add them first
                    if list_items:
                        rich_text_parts.append("\n".join(list_items))
                        list_items = []

                    code_text = _parse_rich_text_elements(element.get("elements", []))
                    rich_text_parts.append(f"```\n{code_text}\n```")

            # Add any remaining list items
            if list_items:
                rich_text_parts.append("\n".join(list_items))

            # Join rich text parts
            if rich_text_parts:
                texts.append(
                    "\n\n".join(part for part in rich_text_parts if part.strip())
                )

        elif block_type == "header":
            if text_obj := block.get("text"):
                texts.append(f"*{text_obj.get('text', '')}*")

        elif block_type == "context":
            context_texts = [
                element.get("text", "")
                for element in block.get("elements", [])
                if element.get("type") in ("mrkdwn", "plain_text")
            ]
            if context_texts:
                texts.append(" ".join(context_texts))

        elif block_type == "divider":
            texts.append("---")

    # Filter out empty texts and join
    result = "\n\n".join(text.strip() for text in texts if text and text.strip())

    # If we didn't get any meaningful content from blocks, fall back to text field
    if not result:
        main_text = message.get("text", "")
        # If we have forwarded content but no main text, use forwarded content
        if not main_text.strip() and forwarded_texts:
            return "\n\n".join(forwarded_texts)
        # If we have both, combine them
        elif main_text.strip() and forwarded_texts:
            return main_text + "\n\n" + "\n\n".join(forwarded_texts)
        # Otherwise just return main text
        else:
            return main_text

    # If we have both main content and forwarded content, combine them
    if forwarded_texts:
        result = result + "\n\n" + "\n\n".join(forwarded_texts)

    return result


def convert_formatting(text: str, user_map: Dict[str, str], migrator=None) -> str:
    """
    Convert Slack-specific markdown to Google Chat compatible format.

    Args:
        text: The Slack message text to convert
        user_map: A dictionary mapping Slack user IDs to Google Chat user IDs/emails
        migrator: Optional migrator instance for tracking unmapped users

    Returns:
        The formatted text with Slack mentions converted to Google Chat format
    """
    if not text:
        return ""

    text = text.replace("&lt;", "<").replace("&gt;", ">").replace("&amp;", "&")

    def replace_user_mention(match: re.Match) -> str:
        slack_user_id = match.group(1)
        gchat_user_id = user_map.get(slack_user_id)

        if gchat_user_id:
            return f"<users/{gchat_user_id}>"

        # Enhanced logging and tracking for unmapped user mentions
        if migrator and hasattr(migrator, "unmapped_user_tracker"):
            current_channel = getattr(migrator, "current_channel", "unknown")
            current_ts = getattr(migrator, "current_message_ts", "unknown")

            # Track this unmapped mention
            migrator.unmapped_user_tracker.track_unmapped_mention(
                slack_user_id, current_channel, current_ts, text
            )

            log_with_context(
                logging.ERROR,
                f"Could not map Slack user ID: {slack_user_id} in message mention (channel: {current_channel})",
                user_id=slack_user_id,
                channel=current_channel,
                message_ts=current_ts,
            )
        else:
            # Fallback to original logging if no migrator/tracker
            log_with_context(
                logging.WARNING, f"Could not map Slack user ID: {slack_user_id}"
            )

        return f"@{slack_user_id}"

    text = re.sub(r"<@([A-Z0-9]+)>", replace_user_mention, text)
    text = re.sub(r"<#C[A-Z0-9]+\|([^>]+)>", r"#\1", text)

    def replace_link(match: re.Match) -> str:
        """
        Replace Slack-formatted links with appropriate formatting for Google Chat.

        In Slack, links are formatted as <url|text>. If the URL and display text
        are identical, this function returns just the URL. Otherwise, it maintains
        the link format expected by Google Chat.

        Args:
            match: A regex match object containing the URL and link text

        Returns:
            Properly formatted link for Google Chat
        """
        url, link_text = match.group(1), match.group(2)
        return url if url == link_text else f"<{url}|{link_text}>"

    text = re.sub(r"<(https?://[^|]+)\|([^>]+)>", replace_link, text)
    text = re.sub(r"<(https?://[^|>]+)>", r"\1", text)
    text = re.sub(r"<!([^|>]+)(?:\|([^>]+))?>", r"@\1", text)
    text = emoji.emojize(text, language="alias")

    return text
