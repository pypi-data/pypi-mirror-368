"""static_sitemap lib"""

from re import findall
from urllib.parse import urlparse
from requests import get
from sys import argv


def is_image(uri):
    """check if image"""
    img_ext = ["png", "jpg", "ico", "gif", "jpeg", "svg"]
    for one_ext in img_ext:
        if uri.endswith(one_ext):
            return True
    return False


def should_check_file(current_url, global_vars):
    """check if file should be checked"""
    if is_image(current_url):
        return False
    for one_ext in global_vars["allowed"]:
        if current_url.endswith(one_ext):
            return True
    for one_ext in global_vars["notallowed"]:
        if current_url.endswith(one_ext):
            return False
    return True


def get_displayer(global_vars=None):
    """display text"""

    def displayer_fn(text, end=""):
        if global_vars is not None and not global_vars["quiet"]:
            if end == "\n":
                print(text)
            else:
                print(text, end="")

    return displayer_fn


def explore_url(url, domain_name, global_vars):
    """explore url"""
    disp = get_displayer(global_vars)
    disp("Exploring " + url, "\n")
    href_in_domain = set()
    href_out_domain = set()
    href_mail = set()
    href_phone = set()
    temp_url = urlparse(url).geturl()
    try:
        response = get(temp_url, timeout=global_vars["timeout"], allow_redirects=True)
    except Exception as exception:
        disp(type(exception).__name__, "\n")
        disp(exception.__class__.__name__, "\n")
        disp(exception.__class__.__qualname__, "\n")
        return False
    web_content = response.text.strip()
    if global_vars["html"]:
        disp(web_content, "\n")
    variable = findall('href="[^"]*"', web_content)
    without_last = "/".join(response.url.split("/")[:-1])
    global_domain = urlparse(url).scheme + "://" + urlparse(url).netloc
    for one_link in variable:
        one_link = one_link.replace("href=", "")
        one_link = one_link.replace(one_link[0], "")
        # sort
        if one_link.startswith("mailto:"):
            href_mail.add(one_link.replace("mailto:", ""))
        elif one_link.startswith("tel:"):
            href_phone.add(one_link.replace("tel:", ""))
        elif one_link.startswith("#"):
            continue
        elif one_link.startswith("?"):
            one_link = response.url.split("?")[0] + one_link
        elif one_link.startswith("./"):
            if response.url.endswith("/"):
                one_link = response.url + one_link[2:]
            else:
                one_link = without_last + one_link[1:]
        elif one_link.startswith("//"):
            one_link = one_link.replace("//", "http://")
        elif one_link.startswith("/"):
            one_link = global_domain + one_link

        if one_link.startswith(domain_name):
            if one_link not in href_in_domain:
                href_in_domain.add(one_link)
        elif one_link not in href_out_domain:
            href_out_domain.add(one_link)
    return href_in_domain, href_out_domain, href_mail, href_phone


def disp_results(global_vars, res):
    """Dispay stats of result"""
    disp = get_displayer(global_vars)
    for one_res_key, values in res.items():
        disp(f">>> {one_res_key} : ")
        disp(len(values), "\n")
        if global_vars["verbose"]:
            for one_link in values:
                disp(one_link, "\n")


NEWS = 'xmlns:news="http://www.google.com/schemas/sitemap-news/0.9"'
XHTML = ' xmlns:xhtml="http://www.w3.org/1999/xhtml"'
IMAGE = 'xmlns:image="http://www.google.com/schemas/sitemap-image/1.1"'
VIDEO = 'xmlns:video="http://www.google.com/schemas/sitemap-video/1.1"'


def write_sitemap(urls):
    """write sitemap"""
    string_to_add = ""
    string_to_add += '<?xml version="1.0" encoding="UTF-8"?>' + "\n"
    string_to_add += (
        f'<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" {NEWS} {XHTML} {IMAGE} {VIDEO}>'
        + "\n"
    )
    for one_link in urls:
        string_to_add += "    <url>\n"
        string_to_add += f"{' ' * 8}<loc>{one_link}</loc>\n"
        string_to_add += f"{' ' * 8}<changefreq>weekly</changefreq>\n"
        string_to_add += f"{' ' * 8}<priority>0.5</priority>\n"
        string_to_add += "    </url>\n"
    string_to_add += "</urlset>"
    with open("sitemap.xml", "w", encoding="utf-8") as f:
        f.write(string_to_add)


def parse_args():
    """parse args"""
    global_vars = {}
    global_vars["verbose"] = True if "--verbose" in argv else False
    global_vars["quiet"] = True if "--quiet" in argv else False
    global_vars["sitemap"] = True if "--sitemap" in argv else False
    global_vars["--rm-error"] = True if "--rm-error" in argv else False
    global_vars["css"] = False if "--css" in argv else True
    global_vars["json"] = False if "--json" in argv else True
    global_vars["html"] = True if "--html" in argv else False
    global_vars["timeout"] = (
        int(argv[argv.index("--timeout") + 1]) if "--timeout" in argv else 5
    )
    global_vars["notallowed"] = ["css", "js", "json", "xml"]
    for one_arg in argv:
        if one_arg.startswith("--notallowed"):
            global_vars["notallowed"].append(one_arg.split("=")[1])

    global_vars["allowed"] = []
    for one_arg in argv:
        if one_arg.startswith("--allowed"):
            global_vars["allowed"].append(one_arg.split("=")[1])

    if len(argv) <= 1:
        print("No arguments were given")
        base_url = ""
    else:
        base_url = argv[1]
    return global_vars, base_url
