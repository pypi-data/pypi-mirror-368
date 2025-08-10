"""static sitemap generator"""

from .lib import (
    get_displayer,
    explore_url,
    disp_results,
    write_sitemap,
    parse_args,  # noqa: F401
    should_check_file,
)


def main(base_url, global_vars):
    """global main function"""
    if base_url == "":
        return
    disp = get_displayer(global_vars)
    href_in_domain = set()
    href_out_domain = set()
    href_mail = set()
    href_phone = set()
    domain_name = base_url.split("/")
    while len(domain_name) > 3:
        domain_name.pop()
    domain_name = "/".join(domain_name)
    domain_name += "/"
    urls_explored = {}
    urls_list = [base_url]
    try:
        idx = 0
        while idx < len(urls_list):
            current_url = urls_list[idx]
            idx += 1
            if should_check_file(current_url, global_vars):
                rest = explore_url(current_url, domain_name, global_vars)
                if rest is False and global_vars["--rm-error"]:
                    href_in_domain.remove(current_url)
                else:
                    for one_link in rest[0]:
                        if one_link not in urls_explored:
                            urls_list.append(one_link)
                            urls_explored[one_link] = False
                    href_in_domain.add(current_url)
                    href_out_domain.update(rest[1])
                    href_mail.update(rest[2])
                    href_phone.update(rest[3])
            urls_explored[current_url] = True

    except KeyboardInterrupt:
        pass
    except Exception as e:
        print(f"Error {e}")

    if not global_vars["quiet"]:
        disp("Finished Exploring", "\n")

    href_in_domain = sorted(href_in_domain)

    if global_vars["sitemap"]:
        write_sitemap(href_in_domain)

    disp_results(
        global_vars,
        {
            "href_in_domain": href_in_domain,
            "href_out_domain": href_out_domain,
            "href_mail": href_mail,
            "href_phone": href_phone,
        },
    )
