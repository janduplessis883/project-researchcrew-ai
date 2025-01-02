import time
from loguru import logger
import dataclasses
import mistune
import notion_client

from researchcrew_ai.notionfier.plugins.footnotes import *
from researchcrew_ai.notionfier.renderer import MyRenderer

from notionhelper import NotionHelper
from researchcrew_ai.secrets.import_secrets import RESEARCH_DATABASE_ID


# Add a file sink for logging
logger.add("logs/app.log", rotation="10 MB", retention="28 days")


# = Decorators =========================================================================================================

def time_it(func):
    def wrapper(*args, **kwargs):
        func_name = func.__name__
        logger.info(f"🖥️    Started: '{func_name}'")
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        elapsed_time = end_time - start_time
        func_name = func.__name__
        logger.info(f"✅ Completed: '{func_name}' ⚡️{elapsed_time:.6f} sec")
        return result

    return wrapper


# Universal functions ==================================================================================================

# Append markdown to Notion page
def append_markdown_to_notion_page(token: str, page_id: str, markdown_content: str):
    """
    Appends Markdown content as blocks to an existing Notion page.

    Args:
        token (str): The Notion auth token.
        page_id (str): The ID of the Notion page where blocks will be appended.
        markdown_content (str): The Markdown content to be processed.

    """
    # Create a Mistune Markdown renderer with plugins
    md = mistune.create_markdown(
        renderer=notionfier.MyRenderer(),
        plugins=[
            mistune.plugins.plugin_task_lists,
            mistune.plugins.plugin_table,
            mistune.plugins.plugin_url,
            mistune.plugins.plugin_def_list,
            mistune.plugins.plugin_strikethrough,
            notionfier.plugins.plugin_footnotes,
        ],
    )
    # Render Markdown content to Notion blocks
    result = md(markdown_content)

    # Convert blocks to the format expected by the Notion API
    children = [
        dataclasses.asdict(
            x, dict_factory=lambda x: {k: v for (k, v) in x if v is not None}
        )
        for x in result
    ]

    # Initialize Notion client
    client = notion_client.Client(auth=token)

    # Append blocks to the specified Notion page
    client.blocks.children.append(block_id=page_id, children=children)


def create_new_notion_page(cpms_id):
    """
    Creates a new page in a Notion database with the given CPMS ID.

    Args:
        cpms_id (str): The CPMS ID to be used as the title and content of the new Notion page.

    Returns:
        str: The ID of the newly created Notion page.
    """
    nh= NotionHelper()

    properties = {"Sponsor":{"title":[{"text":{"content":cpms_id}}]},"CPMS ID":{"rich_text":[{"text":{"content":cpms_id}}]}}

    response = nh.new_page_to_db(RESEARCH_DATABASE_ID, page_properties=properties)
    return response['id']


def read_md_file(file_path):
    """
    Reads the content of a Markdown file, removes Markdown code block delimiters, and returns the cleaned text.

    Args:
        file_path (str): The path to the Markdown file to be read.

    Returns:
        str: The content of the file with Markdown code block delimiters removed.
    """
    # Get page content from MardDown File
    with open(file_path, 'r', encoding='utf-8') as file:
        text_01 = file.read()

    # Check Format of downloaded Text
    text_01 = text_01.replace("```markdown", "").replace("```", "")

    return text_01
