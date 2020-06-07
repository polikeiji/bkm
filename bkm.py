import click
import yaml
import webbrowser
import os
import os.path
import pathlib
import logging
 
logger = logging.getLogger(__name__)
log_format = '%(asctime)s [%(levelname)s] (%(filename)s:%(funcName)s:%(lineno)d) %(message)s'
streamHandler = logging.StreamHandler()
streamHandler.setFormatter(logging.Formatter(log_format))
logger.addHandler(streamHandler)
 
reserved_keywords = ['a', 'd', 'g']
bookmarks = {}
bkm_file = None
 

def _load_bookmarks(ctx: click.Context):
    global bookmarks, bkm_file
    # The bkm_file is hard coded because Context isn't setup yet in MultiCommand.list_commands.
    #bkm_file = ctx.params['bookmark_file']\
    bkm_file = os.environ.get('BOOKMARKS', os.path.join(pathlib.Path.home(), '.bookmarks'))
    if len(bookmarks) == 0 and os.path.exists(bkm_file):
        with open(bkm_file, 'r') as bkm_file_stream:
            bookmarks = yaml.load(bkm_file_stream, Loader=yaml.FullLoader)
 
def _get_keys(ctx: click.Context):
    keys = []
    here = ctx
    while here is not None:
        if here.parent is not None:
            keys.append(here.command.name)
        here = here.parent
    keys.reverse()
    return keys
 
def _search_bookmark_def(ctx: click.Context):
    _load_bookmarks(ctx)
    keys = _get_keys(ctx)
    bookmark_def = bookmarks
    for name in keys:
        bookmark_def = bookmark_def[name]
    return bookmark_def
 
def _update_bookmark_def():
    with open(bkm_file, 'w+') as bkm_file_stream:
        bkm_file_stream.write(yaml.dump(bookmarks))
 
def _add_callback(here, name, url, description=None):
    new_bkm = {}
    here[name] = {
        '_name': name,
        '_url': url,
        '_description': description,
    }
    _update_bookmark_def()
    click.echo('Add a new bookmark [{} ({})]'.format(name, url))
 
def _delete_callback(here, name):
    del(here[name])
    _update_bookmark_def()
    click.echo('Delete a group [{}]'.format(name))
 
def _group_callback(here, name, description):
    is_update = name in here
    if not is_update:
        here[name] = {
            '_name': name,
            '_group': True,
            '_description': description,
        }
    else:
        here[name]['_description'] = description
    _update_bookmark_def()
    if not is_update:
        click.echo('Add a new group [{}]'.format(name))
    else:
        click.echo('Update a group [{}]'.format(name))
 

class BKMGroup(click.MultiCommand):
 
    def __init__(self, name=None, bookmark_def=None, **kwargs):
        click.MultiCommand.__init__(self, name, **kwargs)
        self.bookmark_def = bookmark_def
 
    def load_bookmarks(self, ctx:click.Context):
        if self.bookmark_def is None:
            self.bookmark_def = _search_bookmark_def(ctx)
 
    def list_commands(self, ctx):
        logger.debug(ctx.params)
        self.load_bookmarks(ctx)
        additional_commands = reserved_keywords if '_url' not in self.bookmark_def else []
        return [k for k in self.bookmark_def.keys() if not k.startswith('_')] + additional_commands
 
    def get_command(self, ctx, name):
        logger.debug(name)
        #logger.debug(self.bookmark_def)
        self.load_bookmarks(ctx)
        if name == 'a':
            return click.Command(
                name=name,
                help='Add a new bookmark',
                callback=lambda name, url, description: _add_callback(self.bookmark_def, name, url, description),
                params=[
                    click.Argument(['name']),
                    click.Argument(['url']),
                    click.Argument(['description'], required=False, default=''),
                ],
            )
        elif name == 'd':
            return click.Command(
                name=name,
                help='Delete a bookmark or a group.',
                callback=lambda name: _delete_callback(self.bookmark_def, name),
                params=[
                    click.Argument(['name']),
                ],
            )
        elif name == 'g':
            return click.Command(
                name=name,
                help='Create a new group.',
                callback=lambda name, description: _group_callback(self.bookmark_def, name, description),
                params=[
                    click.Argument(['name']),
                    click.Argument(['description'], required=False, default=''),
                ],
            )
        elif name in self.bookmark_def:
            if '_group' in self.bookmark_def[name] and self.bookmark_def[name]['_group']:
                return BKMGroup(
                    name=name,
                    bookmark_def=self.bookmark_def[name],
                    help='[g] {}'.format(self.bookmark_def[name]['_description']),
                )
            else:
                return click.Command(
                    name=self.bookmark_def[name]['_name'],
                    callback=lambda:\
                        webbrowser.open(self.bookmark_def[name]['_url'])\
                            if self.bookmark_def[name].get('_url') is not None\
                            else None,
                    help=self.bookmark_def[name]['_description'] if '_description' in self.bookmark_def[name] else None,
                )
        return None
 

@click.command(cls=BKMGroup)
@click.pass_context
@click.option(
    '-f',
    '--bookmark-file',
    default=os.path.join(pathlib.Path.home(), '.bookmarks'),
    help='Location of a YAML format bookmarks.'
)
@click.option(
    '--debug',
    default=False,
    is_flag=True,
)
def bkm(ctx, bookmark_file, debug):
    if debug:
        logger.setLevel(logging.DEBUG)
 
if __name__ == '__main__':
    bkm()
