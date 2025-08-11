# Copyright 2020 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import requests
import json
import os


shortlink_edge = {
    'color': {
        'color': '#E7572C'
    },
    'title': 'URL Shortener Parser',
    'label': '🔗'
}
  

def expand_bitly_url(bitlink_id, api_key):
    # Ref: https://dev.bitly.com/v4/

    r = requests.post(
        'https://api-ssl.bitly.com/v4/expand',
        data=json.dumps({'bitlink_id': f'bit.ly/{bitlink_id.rstrip("/")}'}),
        headers={'Content-Type': 'application/json', 'Authorization': f'Bearer {api_key}'})

    if r.status_code == 200:
        return r.json()
    else:
        return {}


def expand_url_via_redirect_header(base_url, shortcode):
    r = requests.get(f'{base_url}{shortcode.rstrip("/")}', allow_redirects=False)

    if r.status_code in [301, 302]:
        return r.headers['Location']
    else:
        return {}


def run(unfurl, node):
    if not unfurl.remote_lookups:
        return

    preceding_domain = unfurl.find_preceding_domain(node)

    # LinkedIn has another method of URL shortening that's different from how most others do it; I can
    # refactor this in the future to be more flexible if I find more sites that operate this way, but for now
    # this works.
    if node.data_type == 'url.query.pair' and node.key == 'code':
        if 'linkedin.com' in preceding_domain:
            expanded_url = expand_url_via_redirect_header('https://www.linkedin.com/slink?code=', node.value)
            if expanded_url:
                unfurl.add_to_queue(
                    data_type='url', key=None, value=expanded_url,
                    label=f'Expanded URL: {expanded_url}',
                    hover='Expanded URL, retrieved from linkedin.com via "Location" header',
                    parent_id=node.node_id, incoming_edge_config=shortlink_edge)
            return

    # Substack inserts a redirect
    if 'substack.com' == preceding_domain and node.key == 2 and \
            unfurl.check_sibling_nodes(node, data_type='url.path.segment', key=1, value='redirect'):
        expanded_url = expand_url_via_redirect_header('https://substack.com/redirect/', node.value)

        if expanded_url:
            unfurl.add_to_queue(
                data_type='url', key=None, value=expanded_url,
                label=f'Expanded URL: {expanded_url}',
                hover=f'Expanded URL, retrieved from {preceding_domain} via "Location" header',
                parent_id=node.node_id, incoming_edge_config=shortlink_edge)

    if node.data_type != 'url.path':
        return

    bitly_domains = ['bit.ly', 'bitly.com', 'j.mp']
    if any(bitly_domain in unfurl.find_preceding_domain(node) for bitly_domain in bitly_domains):
        expanded_info = expand_bitly_url(node.value[1:], unfurl.api_keys.get('bitly', os.environ.get('bitly')))

        if not expanded_info:
            return

        node.hover = 'Bitly Short Links can be expanded via the Bitly API to show the ' \
                     '"long" URL and the creation time of the short-link.' \
                     '<a href="https://dev.bitly.com/v4/#operation/expandBitlink" ' \
                     'target="_blank">[ref]</a>'

        if expanded_info['created_at'].endswith('+0000'):
            expanded_info['created_at'] = expanded_info['created_at'][:-5]

        if expanded_info['created_at'][10] == 'T':
            expanded_info['created_at'] = f'{expanded_info["created_at"][:10]} {expanded_info["created_at"][11:]}'

        unfurl.add_to_queue(
            data_type='description', key=None, value=expanded_info['created_at'],
            label=f'Creation Time:\n{expanded_info["created_at"]}',
            hover='Short-link creation time, retrieved from Bitly API',
            parent_id=node.node_id, incoming_edge_config=shortlink_edge)

        unfurl.add_to_queue(
            data_type='url', key=None, value=expanded_info['long_url'],
            label=f'Expanded URL: {expanded_info["long_url"]}', hover='Expanded URL, retrieved from Bitly API',
            parent_id=node.node_id, incoming_edge_config=shortlink_edge)

        return

    redirect_expands = [
        {'domain': 'bit.do', 'base_url': 'https://bit.do/'},
        {'domain': 'buff.ly', 'base_url': 'https://buff.ly/'},
        {'domain': 'cutt.ly', 'base_url': 'https://cutt.ly/'},
        {'domain': 'db.tt', 'base_url': 'https://db.tt/'},
        {'domain': 'dlvr.it', 'base_url': 'https://dlvr.it/'},
        {'domain': 'fb.me', 'base_url': 'https://fb.me/'},
        {'domain': 'flip.it', 'base_url': 'https://flip.it/'},
        {'domain': 'goo.gl', 'base_url': 'https://goo.gl/'},
        {'domain': 'ift.tt', 'base_url': 'https://ift.tt/'},
        {'domain': 'is.gd', 'base_url': 'https://is.gd/'},
        {'domain': 'lc.chat', 'base_url': 'https://lc.chat/'},
        {'domain': 'lnkd.in', 'base_url': 'https://www.linkedin.com/slink?code='},
        {'domain': 'nyti.ms', 'base_url': 'https://nyti.ms/'},
        {'domain': 'ow.ly', 'base_url': 'http://ow.ly/'},
        {'domain': 'reut.rs', 'base_url': 'https://reut.rs/'},
        {'domain': 'sansurl.com', 'base_url': 'https://sansurl.com/'},
        {'domain': 'snip.ly', 'base_url': 'https://snip.ly/'},
        {'domain': 't.co', 'base_url': 'https://t.co/'},
        {'domain': 't.ly', 'base_url': 'https://t.ly/'},
        {'domain': 'tinyurl.com', 'base_url': 'https://tinyurl.com/'},
        {'domain': 'tr.im', 'base_url': 'https://tr.im/'},
        {'domain': 'trib.al', 'base_url': 'https://trib.al/'},
        {'domain': 'urlwee.com', 'base_url': 'https://urlwee.com/'},
        {'domain': 'urlzs.com', 'base_url': 'https://urlzs.com/'}
    ]

    for redirect_expand in redirect_expands:
        if redirect_expand['domain'] == preceding_domain:
            expanded_url = expand_url_via_redirect_header(redirect_expand['base_url'], node.value[1:])
            if expanded_url:
                unfurl.add_to_queue(
                    data_type='url', key=None, value=expanded_url,
                    label=f'Expanded URL: {expanded_url}',
                    hover=f'Expanded URL, retrieved from {redirect_expand["domain"]} via "Location" header',
                    parent_id=node.node_id, incoming_edge_config=shortlink_edge)
            return

    # Get the list of "known" URL shortener domains from MISP; many of these seem to be deprecated.
    # Try to expand the shortlink via a 301/302 Location header; if the site uses something like a meta refresh,
    # this won't work.
    misp_shortener_domains = unfurl.known_domain_lists['List of known URL Shorteners domains'].list
    if preceding_domain in misp_shortener_domains:
        expanded_url = expand_url_via_redirect_header(f'https://{preceding_domain}/', node.value[1:])
        if expanded_url:
            unfurl.add_to_queue(
                data_type='url', key=None, value=expanded_url,
                label=f'Expanded URL: {expanded_url}',
                hover=f'Expanded URL, retrieved from {preceding_domain} via "Location" header',
                parent_id=node.node_id, incoming_edge_config=shortlink_edge)
