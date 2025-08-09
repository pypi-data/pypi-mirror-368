# Copyright 2023 OpenSynergy Indonesia
# Copyright 2023 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
# flake8: noqa: B902
import logging

from odoo import http

from odoo.addons.http_routing.models.ir_http import slug
from odoo.addons.website.models.ir_http import sitemap_qs2dom
from odoo.addons.website_slides.controllers.main import WebsiteSlides

_logger = logging.getLogger(__name__)


class WebsiteSlidesSsi(WebsiteSlides):
    def sitemap_slide(env, rule, qs):
        Channel = env["slide.channel"]
        dom = sitemap_qs2dom(qs=qs, route="/slides/", field=Channel._rec_name)
        dom += env["website"].get_current_website().website_domain()
        for channel in Channel.search(dom):
            loc = "/slides/%s" % slug(channel)
            if not qs or qs.lower() in loc:
                yield {"loc": loc}

    @http.route(
        [
            '/slides/<model("slide.channel"):channel>',
            '/slides/<model("slide.channel"):channel>/page/<int:page>',
            '/slides/<model("slide.channel"):channel>/tag/<model("slide.tag"):tag>',
            '/slides/<model("slide.channel"):channel>/tag/<model("slide.tag"):tag>/page/<int:page>',
            '/slides/<model("slide.channel"):channel>/category/<model("slide.slide"):category>',
            '/slides/<model("slide.channel"):channel>/category/<model("slide.slide"):category>/page/<int:page>',
        ],
        type="http",
        auth="public",
        website=True,
        sitemap=sitemap_slide,
    )
    def channel(
        self,
        channel,
        category=None,
        tag=None,
        page=1,
        slide_type=None,
        uncategorized=False,
        sorting=None,
        search=None,
        **kw
    ):
        if not sorting:
            sorting = "sequence"
        res = super().channel(
            channel=channel,
            category=category,
            tag=tag,
            page=page,
            slide_type=slide_type,
            uncategorized=uncategorized,
            sorting=sorting,
            search=search,
            **kw
        )
        return res
