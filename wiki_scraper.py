import base64

import requests  # pip install requests
from bs4 import BeautifulSoup  # pip install beautifulsoup4


def fetch_creature_detail_page_links() -> list:
    """This method retrieves all links to the Space Creatures detail pages from the wiki.
    It searches the wiki page for all links pointing to the Space Creatures' detail pages and returns a list of these links.
    These links can then be used to access the Space Creatures' detail pages and get more information about them.

    Returns:
        list: List of strings, each containing a URL of a Space Creature detail page in the wiki.
    """

    # 1. fetch HTML of the Space Creatures Wiki page
    wiki_base_url = "https://thessum.miraheze.org"
    wiki_space_creatures_url = wiki_base_url + "/wiki/Space_Creatures"
    response = requests.get(wiki_space_creatures_url)
    html = response.content

    # 2. find all Space Creatures in the HTML by elements/characteristics used only for and by all Space Creatures entries on the page

    soup = BeautifulSoup(html, "html.parser")
    gallerytext_elements = soup.find_all("div", class_="gallerytext")

    # 3. find all links to the detail pages of the Space Creatures in the entries
    detail_page_urls = []

    for gallerytext_element in gallerytext_elements:
        a = gallerytext_element.find("a")

        # https://beautiful-soup-4.readthedocs.io/en/latest/index.html?highlight=attributes#attributes
        href = a.get("href")
        if href:
            detail_page_urls.append(wiki_base_url + href)

    return detail_page_urls


def fetch_creature_info(detail_page_url: str) -> dict:
    """This method retrieves selected information of a Space Creature from its detail page in the Wiki.

    Args:
        detail_page_url (str): URL of a Space Creature detail page in the wiki.

    Returns:
        dict: Information of the Space Creature as a dictionary. If the table in the wiki is complete, the dictionary contains the keys: wiki_url (str), number (int or str), name (str), personality (str), likes (list), dislikes (list), image_url (str), image_alt (str), attribution (str).
    """

    # 1. fetch HTML of the detail page
    response = requests.get(detail_page_url)
    html = response.content

    # 2. find the two tables that contain the creature information
    soup = BeautifulSoup(html, "html.parser")
    tables = soup.find_all("table", class_="wikitable")

    # 3. read the basic information about the creature from the first table
    info_dict = {"wiki_url": detail_page_url}

    if len(tables) < 1:
        return info_dict

    table1_cells = tables[0].find_all("td")

    for i, cell in enumerate(table1_cells):
        if "TBA" in cell.text:
            continue
        if i == 0:
            try:
                info_dict["number"] = int(cell.text)
            except ValueError:
                info_dict["number"] = cell.text
        elif i == 1:
            info_dict["name"] = cell.text
        elif i == 3:
            info_dict["personality"] = cell.text

    # 4. read the likes and dislikes of the creature from the 2nd table
    if len(tables) < 2:
        return info_dict

    likes = []
    dislikes = []

    table2_cells = tables[1].find_all("td")

    if len(table2_cells) < 4:
        return info_dict

    compatibility_cell = table2_cells[5]
    if compatibility_cell.text.strip() != "TBA":
        for compatibility_info in compatibility_cell.text.split("\n"):
            if compatibility_info and "TBA" not in compatibility_info:

                key, values = compatibility_info.split(":")[0:2]
                creatures = [c.strip() for c in values.split(",")]
                likes += creatures if "likes" in key.lower() else []
                dislikes += creatures if "dislikes" in key.lower() else []

    info_dict["likes"] = likes
    info_dict["dislikes"] = dislikes

    # 5. read the src url for the creature image and the corresponding alt text
    img = soup.find("img")
    if img:
        info_dict["image_url"] = f"https:{img.get('src')}"
        info_dict["image_alt"] = img.get("alt")

        # 5.1 fetch the image of the creature and generate a DataURL from it
        response = requests.get(info_dict["image_url"])
        if response.status_code == 200:
            image_bytes = response.content
            image_base64 = base64.b64encode(image_bytes).decode("utf-8")
            info_dict["image_url"] = f"data:image/png;base64,{image_base64}"

    # 7. generate attribution text
    detail_page_name = detail_page_url.split("/")[-1]
    info_dict[
        "attribution"
    ] = f'Information on/pictures of the creature(s) are from the <a href="https://thessum.miraheze.org/wiki/Main_Page">The Ssum: Forbidden Lab\'s Unofficial Miraheze Wiki</a>. Authors of the Wiki article <a href="{detail_page_url}">{detail_page_name.replace("_", " ")}</a> are <a href="https://thessum.miraheze.org/w/index.php?title={detail_page_name}&action=history">The Ssum: Forbidden Lab\'s Unofficial Miraheze Wiki and contributors</a>. Provided under the licence <a href="https://creativecommons.org/licenses/by-sa/4.0/">Creative Commons Attribution-ShareAlike 4.0 International (CC BY-SA 4.0)</a>.'

    return info_dict


def print_creature_info(creature_info: dict) -> None:
    """Prints information about a Space Creature.

    Args:
        creature_info (dict): Dictionary containing the creature's wiki_url, number, name, personality, likes, dislikes, image_url, image_alt, and an attribution to its wiki page
    """

    print()
    print(
        f"No. {creature_info.get('number')} | Name: {creature_info.get('name')} | Personality: {creature_info.get('personality')}"
    )
    print(f"Likes: {creature_info.get('likes')}")
    print(f"Dislikes: {creature_info.get('dislikes')}")
    print(f"Wiki URL: {creature_info.get('wiki_url')}")
    print(f"Image URL: {creature_info.get('image_url')}")
    print(f"Image alt: {creature_info.get('image_alt')}")
    print(f"Attribution: {creature_info.get('attribution')}")


if __name__ == "__main__":
    detail_page_urls = fetch_creature_detail_page_links()
    for url in detail_page_urls:
        print_creature_info(fetch_creature_info(url))
