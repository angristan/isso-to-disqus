# Migrate Isso comments to Disqus

This tool generates an [Disqus-compatible WXR-like XML file](https://help.disqus.com/en/articles/1717222-custom-xml-import-format) from an Isso SQLite database file.

## Usage

Dependencies:

* Python 3

```
git clone https://github.com/angristan/isso-to-disqus.git
cd isso-to-disqus
pip install -r requirements.txt
```

Now copy the sqlite (`.db`) file from your Isso server into the folder.

Get your XML export:

```
export WEBSITE_URL=https://blog.tld DB_FILE_PATH=comments.db
python isso-to-disqus.py
```

Once you create a new Disqus community, you can import the XML file from the settings, or [import.disqus.com](https://import.disqus.com/).
