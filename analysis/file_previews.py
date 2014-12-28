embed_code = {
    '.jpg': r'''
        <img src="{url}" style="max-width: 95%;"/>
    ''',
    '.gif': r'''
        <img src="{url}" style="max-width: 95%;"/>
    ''',
    '.png': r'''
        <img src="{url}" style="max-width: 95%;"/>
    ''',
    '.svg': r'''
        <img src="{url}" style="max-width: 95%;"/>
    ''',
    '.bmp': r'''
        <img src="{url}" style="max-width: 95%;"/>
    ''',
    '.ico': r'''
        <img src="{url}" style="max-width: 95%;"/>
    ''',
    '.cdf': r'''
        <div style="height: 500px; width: 85%; max-width: 100%;  overflow: auto; resize: both;">
        <embed src="{url}" style="height:3000px; width:100%;"/>
        </div>
    ''',
    '.m': r'''
        <div style="height: 500px; width: 85%; max-width: 100%; overflow: auto; resize: both; border-style: solid; background-color: white;">
        <pre><code>{content}</code></pre>
        </div>
        
        <script>
        hljs.initHighlighting();
        </script>
    ''',
    '.py': r'''
        <div style="height: 500px; width: 85%; max-width: 100%; overflow: auto; resize: both; border-style: solid; background-color: white;">
        <pre><code>{content}</code></pre>
        </div>
        
        <script>
        hljs.initHighlighting();
        </script>
    ''',
    '.json': r'''
        <div style="height: 500px; width: 85%; max-width: 100%; overflow: auto; resize: both; border-style: solid; background-color: white;">
        <pre><code>{content}</code></pre>
        </div>
        
        <script>
        hljs.initHighlighting();
        </script>
    ''',
    '.js': r'''
        <div style="height: 500px; width: 85%; max-width: 100%; overflow: auto; resize: both; border-style: solid; background-color: white;">
        <pre><code>{content}</code></pre>
        </div>
        
        <script>
        hljs.initHighlighting();
        </script>
    ''',
    '.txt': r'''
        <div style="height: 500px; width: 85%; max-width: 100%; overflow: auto; resize: both; border-style: solid; background-color: white;">
        <pre><code>{content}</code></pre>
        </div>
    ''',
    '.csv': r'''
        <div style="height: 500px; width: 85%; max-width: 100%; overflow: auto; resize: both; border-style: solid; background-color: white;">
        <pre><code>{content}</code></pre>
        </div>
    ''',
}