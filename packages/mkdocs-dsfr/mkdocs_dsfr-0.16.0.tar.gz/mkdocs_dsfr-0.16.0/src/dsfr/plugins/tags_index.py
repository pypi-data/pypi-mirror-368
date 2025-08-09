from mkdocs.plugins import BasePlugin
import importlib.resources
from mkdocs.structure.files import File


class TagsIndexPlugin(BasePlugin):

    colors = [
        "green-menthe",
        "brown-cafe-creme",
        "blue-ecume",
        "pink-macaron",
        "yellow-tournesol",
        "purple-glycine",
        "beige-gris-galet",
        "green-bourgeon",
        "brown-caramel",
        "blue-cumulus",
        "pink-tuile",
        "yellow-moutarde",
        "green-emeraude",
        "orange-terre-battue",
        "brown-opera",
        "green-tilleul-verveine",
        "green-archipel"
    ]
    def on_config(self, config):
        self.tags_index = {}

    def on_files(self, files, /, *, config):
        with importlib.resources.path('dsfr.plugins.templates', 'tags_index.md') as template_path:
            # Créer un objet File qui référence ce fichier template
            tags_file = File(
                path='tags_index.md',
                src_dir=str(template_path.parent),
                dest_dir=next(iter(files)).dest_dir,
                use_directory_urls=config['use_directory_urls']
            )
            files.append(tags_file)
        return files

    def on_page_markdown(self, markdown, /, *, page, config, files):
        tags = page.meta.get('tags', [])
        for tag in tags:
            self.tags_index.setdefault(tag, []).append(page)
        return markdown

    def on_env(self, env, /, *, config, files):
        for i, tag in enumerate(sorted(self.tags_index.keys())):
            color = self.colors[i % len(self.colors)]
            self.tags_index[tag] = {
                'pages': self.tags_index[tag],
                'color': color,
            }
        env.globals['tags_index'] = self.tags_index
        return env
