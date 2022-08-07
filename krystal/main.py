import os
from flask_frozen import Freezer, relative_url_for
from flask import Flask, render_template, url_for
import argparse
import time
from marko import Markdown,inline, block, html_renderer

from datetime import datetime
now = datetime.now()


orig_render_image = html_renderer.HTMLRenderer.render_image


my_url_for = url_for

def hook_render_image(self, element):
    if not element.dest.startswith('http:') and not element.dest.startswith('https:'):
        element.dest = my_url_for('static', filename=element.dest)
    return orig_render_image(self, element)


html_renderer.HTMLRenderer.render_image = hook_render_image

CWD = os.getcwd()
post_dir = CWD+'/_posts/'
app = Flask(__name__, template_folder=f'{CWD}/templates', static_folder=f'{CWD}/static')
freezer = Freezer(app)



block.ThematicBreak.match = lambda x: False
block.Paragraph.is_setext_heading = lambda x: False

class TitleEntry(inline.InlineElement):
    pattern = r'---\nlayout: *post\ntitle: "(.*)"\ndescription: *"(.*)"\ncreated: *(.*)\nmodified: *(.*)\ntags: *\[(.*)\]\n((.*)\n)*---'
    parse_children = False

    def __init__(self, match):
        self.title = match.group(1)
        self.description = match.group(2)
        self.created = match.group(3)
        self.modified = match.group(4)
        self.tags = match.group(5)

class TitleEntryRendererMixin(object):
    def render_title_entry(self, element):
        return f'<h1 id="post-title">{element.title}</h1>'


class YoutubeEntry(inline.InlineElement):
    pattern = r'{\.video (.*)}'
    parse_children = False

    def __init__(self, match):
        self.link = match.group(1)

class YoutubeEntryRendererMixin(object):

    def render_youtube_entry(self, element):
        return f'<div class="youtube-container"><iframe src="{element.link}" frameborder="0" allowfullscreen class="youtube-video"></iframe></div>'

class NewExt:
    elements = [YoutubeEntry]
    renderer_mixins = [YoutubeEntryRendererMixin]

class KrystalExt:
    elements = [TitleEntry]
    renderer_mixins = [TitleEntryRendererMixin]


class BlogEntry:

    def __init__(self, id, created_timestamp, modified_timestamp, title, description, url):
        self.id = id
        self.timestamp = created_timestamp
        self.modified_timestamp = modified_timestamp
        self.title = title
        self.description = description
        self.url = url

def list_entries():
    posts = os.listdir(post_dir)
    posts = filter(lambda x: x.endswith('.md'), posts)
    posts = map(lambda x: x[:-3], posts)
    posts = list(posts)

    #entries = [BlogEntry(now, x, my_url_for('serve_post', post_id=x)) for x in posts]
    entries = []
    for post in posts:
        marko = Markdown(extensions=[KrystalExt, NewExt, 'codehilite'])
        parsed = marko.parse(open(f'{post_dir}/{post}.md').read())

        first = parsed.children[0].children[0]
        if not isinstance(first, TitleEntry):
            raise ValueError('First element should be title entry')

        year, month, day = tuple(map(lambda x: int(x), first.created.split('-')))
        created = datetime(year=year, month=month, day=day)
        year, month, day = tuple(map(lambda x: int(x), first.modified.split('-')))
        modified = datetime(year=year, month=month, day=day)
        entries.append(BlogEntry(post, created, modified, first.title, first.description, my_url_for('serve_post', post_id=post)))


    entries.sort(key=lambda x: (x.timestamp, x.title), reverse=True)
    return entries

@app.route('/about/')
def about():
    return render_template('about.html', now=now)

@app.route('/<post_id>/')
def serve_post(post_id):
    if post_id == 'favicon.ico':
        return ''
    marko = Markdown(extensions=[KrystalExt, NewExt, 'codehilite'])

    parsed = marko.parse(open(f'{post_dir}/{post_id}.md').read())
    first = parsed_title = parsed.children[0].children[0]
    parsed_title = first.title
    parsed_desc = first.description
    post = marko.render(parsed)
    return render_template('post.html', now=now, post=post, post_title=parsed_title, post_description=parsed_desc)

@app.route('/feed.xml')
def serve_feed():
    return render_template('feed.xml', entries=list_entries(), now=now), {
        'Content-Type': 'application/atom+xml; charset=UTF-8',
    }

@app.route('/')
def serve_main():
    return render_template('index.html', entries=list_entries(), now=now)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--port', type=int, default=8080, required=False)
    parser.add_argument('--build', default=False, required=False, action='store_true')
    parser.add_argument('--base-url', type=str, default=None, required=False)

    res = parser.parse_args()
    app.config['TEMPLATES_AUTO_RELOAD'] = True
    app.config['FREEZER_RELATIVE_URLS'] = True
    app.config['FREEZER_DESTINATION'] = f'{CWD}/build'
    if res.base_url:
        from urllib.parse import urlparse
        base_url = urlparse(res.base_url)
        if base_url.scheme:
            app.config['PREFERRED_URL_SCHEME'] = base_url.scheme
        if base_url.netloc:
            app.config['SERVER_NAME'] = base_url.netloc
        if base_url.path:
            app.config['APPLICATION_ROOT'] = base_url.path

    if res.build:
        global my_url_for
        my_url_for = relative_url_for
        freezer.freeze()
    else:
        app.run('0.0.0.0', res.port, debug=True)

if __name__ == '__main__':
    exit(main())
