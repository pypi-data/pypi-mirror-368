"""main func for static_sitemap package"""

from . import main, parse_args

if __name__ == "__main__":
    parsed_global_vars, base_url = parse_args()
    main(base_url, parsed_global_vars)
