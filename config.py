"""Configuration settings for HelpScout data fetcher"""
import os
from dotenv import load_dotenv

load_dotenv()

CLIENT_ID = os.environ.get("HELPSCOUT_CLIENT_ID")
CLIENT_SECRET = os.environ.get("HELPSCOUT_CLIENT_SECRET")

MAILBOX_ID = 21530
PLUGINS_TAGS = ["feedzy","hyve","lightstart","menu-icons","mpg","multiple pages generator","optimole","orbit fox","otter","ppom","redirection-cf7","redirection for cf7","revive old post","revive-old-post","revive social","sparks","super-page-cache","super page cache pro","templates-cloud","visualizer","wpcf7","wp full pay","wplandingkit","wp landing kit","wp-media-library","masteriyo"]
THEMES_TAGS = ["neve","hestia","fse","jaxon","raft","zelle","fork","zerif","riverbank","church-fse"]
WORDPRESS_TICKETS_TAGS = "wporg"
SHOP_TAGS = ["shop-isle-pro","shopisle-pro"]
PAYMENT = "optionistics"