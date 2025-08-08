import json
from IPython.display import HTML, display
import uuid

class NERAnnotator():
    """
    Class for interactively annotating named entities (NER) in a text list within a Jupyter Notebook environment.

    This class allows you to view and annotate entities in text, customize entity types and colors,
    and track the annotation session with a unique identifier.
    This class is linked to Python only through Input; all output is managed by
    JavaScript, so it is not possible to bring annotated entities into Python without copying them.

    Args:
        texts(list): List of strings containing the texts to be annotated. Must be a non-empty list.
        entity_types(list, optional): List of entity types to be annotated (e.g., ['Person', 'Location']).
            If not provided, uses ['Person', 'Location', 'Organization', 'Date', 'Other'] as the default.
        custom_colors(dict, optional): Dictionary that maps each entity type to a hexadecimal color (e.g., {'Person': '#ffeb3b'}).
            If not provided, default colors will be automatically assigned based on entity types.
        session_id (str, optional): Annotation session ID. If not provided, it will be automatically generated.

    Returns:
        (None) The function returns no arguments.

    Raises:
    AssertionError: If `texts` is not a list or is empty.
    """

    def __init__(self, texts, entity_types: list=None, custom_colors: dict=None, session_id=None):
        assert isinstance(texts, list) and len(texts) > 0, "texts must be a non-empty list"
        self.texts = texts
        self.current_index = 0
        self.entities_by_text = {} 

        if entity_types is None:
            entity_types = ['Person', 'Location', 'Organization', 'Date', 'Other']
        self.entity_types = entity_types

        if custom_colors is None:
            base_colors = ['#ffeb3b', '#4caf50', '#2196f3', '#ff9800', '#9c27b0']
            custom_colors = {entity_types[i]: base_colors[i % len(base_colors)] for i in range(len(entity_types))}
        self.custom_colors = custom_colors

        if session_id is None:
            session_id = str(uuid.uuid4())[:8]
        self.session_id = session_id

        self.legend_html = " ".join([
            f'<span style="background:{color}; padding:3px 8px; border-radius:4px; margin:0 5px; color:#000000;">{etype}</span>'
            for etype, color in self.custom_colors.items()
        ])

    def render(self):
        """Renders the annotation interface."""
        # Renders the main container and all texts at once
        self._render_full_interface()

    def _render_full_interface(self):
        # Main container with navigation
        main_html = f"""
        <div id="ner_main_{self.session_id}" style="font-family:Arial; padding:20px;">
            <h2>🏷️ NERNotebook</h2>
            
            <!-- Navigation -->
            <div style="background:#e3f2fd; padding:12px; border-radius:6px; margin-bottom:10px; display:flex; justify-content:space-between; align-items:center;">
                <div style="color:#000000;">
                    <b>📖 Instructions:</b> Select text → Choose type → Click "Mark"
                </div>
                <div>
                    <button id="btnPrev_{self.session_id}" style="padding:5px 12px; background:#757575; color:white; border:none; border-radius:4px; margin-right:10px;">← Previous</button>
                    <span id="textCounter_{self.session_id}" style="margin:0 10px; font-weight:bold; color:#000000;">Text 1 of {len(self.texts)}</span>
                    <button id="btnNext_{self.session_id}" style="padding:5px 12px; background:#757575; color:white; border:none; border-radius:4px;">Next →</button>
                </div>
            </div>

            <!-- Container for texts -->
            <div id="textsContainer_{self.session_id}">
                <!-- Texts will be inserted here by JS -->
            </div>

            <!-- Global buttons -->
            <div style="text-align:center; margin-top:20px;">
                <button id="btnDownloadAll_{self.session_id}" style="padding:10px 20px; background:#2196f3; color:white; border:none; border-radius:4px; font-size:16px; margin-right:10px;">📥 Download All Annotations</button>
                <button id="btnCopyAll_{self.session_id}" style="padding:10px 20px; background:#17a2b8; color:white; border:none; border-radius:4px; font-size:16px;" title="Copy all notes to clipboard">📋 Copy Notes</button>
            </div>

            <!-- Legend -->
            <div style="background:#f0f0f0; padding:10px; border-radius:4px; margin:10px 0; color:#000000;">
                <b>Legend:</b> {self.legend_html}
            </div>
            
            <iframe src="https://ghbtns.com/github-btn.html?user=danttis&repo=NER-Notebook-Annotation&type=watch&count=true&size=large&v=2" frameborder="0" scrolling="0" width="170" height="30" title="GitHub"></iframe>        
            </div>
        """

        #display(HTML(main_html))
        
        js_code = f"""
        <script>
        (function() {{
            const sessionId = '{self.session_id}';
            const texts = {json.dumps(self.texts)};
            const entityTypes = {json.dumps(self.entity_types)};
            const customColors = {json.dumps(self.custom_colors)};
            let currentIndex = 0;

            const textsContainer = document.getElementById('textsContainer_' + sessionId);
            const textCounter = document.getElementById('textCounter_' + sessionId);
            const btnPrev = document.getElementById('btnPrev_' + sessionId);
            const btnNext = document.getElementById('btnNext_' + sessionId);

           // Function to create the HTML of an individual annotator
            function createAnnotatorHTML(text, textIndex) {{
                const textId = sessionId + '_' + textIndex;
                const storageKey = 'ner_' + textId;
                
                return `
                <div id="annotator_${{textId}}" style="display: none;">
                    <div style="background:#f9f9f9; padding:10px; border-radius:4px; margin-bottom:10px; color:#000000;">
                        <b>🆔 Text ID:</b> <code>${{textId}}</code>
                    </div>
                    
                    <div id="text_${{textId}}" contenteditable="false" style="
                        font-size:18px; 
                        padding:20px; 
                        border:2px dashed #2196f3; 
                        border-radius:10px;
                        background: #fefefe;
                        line-height:1.6;
                        user-select:text;
                        cursor:text;
                        color:#000000;">
                        ${{text}}
                    </div>
                    
                    <div style="margin:10px 0;">
                        <label for="type_${{textId}}">Type:</label>
                        <select id="type_${{textId}}">
                            ${{Object.entries(customColors).map(([etype, color]) => 
                                `<option style="background:${{color}};" value="${{etype}}">${{etype}}</option>`
                            ).join('')}}
                        </select>
                        <button id="btnMark_${{textId}}" style="margin-left:10px; padding:5px 12px; background:#4caf50; color:white; border:none; border-radius:4px;">Mark Selection</button>
                        <button id="btnClear_${{textId}}" style="margin-left:5px; padding:5px 12px; background:#f44336; color:white; border:none; border-radius:4px;">Clear All</button>
                        <button id="btnDownload_${{textId}}" style="margin-left:5px; padding:5px 12px; background:#2196f3; color:white; border:none; border-radius:4px;">📥 Download This</button>
                    </div>
                    
                    <pre id="output_${{textId}}" style="margin-top:20px; background:#f5f5f5; padding:10px; border-radius:6px; color:#000000; max-height:200px; overflow:auto;"></pre>
                    
                </div>
                `;
            }}

            // Function to initialize an annotator's event listeners
            function initializeAnnotator(textIndex) {{
                const textId = sessionId + '_' + textIndex;
                const storageKey = 'ner_' + textId;
                const originalText = texts[textIndex];
                let entities = [];

                // Load localStorage
                try {{
                    const stored = localStorage.getItem(storageKey);
                    if (stored) {{
                        entities = JSON.parse(stored);
                    }}
                }} catch (e) {{
                    console.error("Error loading localStorage:", e);
                }}

                const output = document.getElementById("output_" + textId);
                const textDiv = document.getElementById("text_" + textId);

                function saveEntities() {{
                    try {{
                        localStorage.setItem(storageKey, JSON.stringify(entities));
                    }} catch (e) {{
                        console.error("Error saving to localStorage:", e);
                    }}
                }}

                function updateDisplay() {{
                    if (entities.length === 0) {{
                        textDiv.innerHTML = originalText;
                        output.textContent = '[]';
                        return;
                    }}

                    entities.sort((a,b) => a.start - b.start);
                    let result = "";
                    let pos = 0;

                    for (let ent of entities) {{
                        if (ent.start < pos) continue;
                        result += originalText.slice(pos, ent.start);
                        let color = customColors[entityTypes[0]];
                        if (customColors[ent.type]) {{
                            color = customColors[ent.type];
                        }}
                        result += `<span style="background-color:${{color}};">${{originalText.slice(ent.start, ent.end)}}</span>`;
                        pos = ent.end;
                    }}
                    result += originalText.slice(pos);
                    textDiv.innerHTML = result;
                    output.textContent = JSON.stringify(entities, null, 2);
                }}

                // Event listeners
                document.getElementById("btnMark_" + textId).onclick = function() {{
                    const sel = window.getSelection().toString().trim();
                    if (!sel) {{
                        alert("No text selected!");
                        return;
                    }}
                    const type = document.getElementById("type_" + textId).value;
                    const start = originalText.indexOf(sel);
                    if (start === -1) {{
                        alert("Selection not found!");
                        return;
                    }}
                    const end = start + sel.length;

                    const idx = entities.findIndex(e => e.start === start && e.end === end);
                    if (idx !== -1) {{
                        entities[idx].type = type;
                    }} else {{
                        entities.push({{ text: sel, type: type, start: start, end: end }});
                    }}
                    updateDisplay();
                    saveEntities();
                }};

                document.getElementById("btnClear_" + textId).onclick = function() {{
                    entities = [];
                    updateDisplay();
                    saveEntities();
                }};

                document.getElementById("btnDownload_" + textId).onclick = function() {{
                    if (entities.length === 0) {{
                        alert("No annotations for this text.");
                        return;
                    }}

                    const blob = new Blob([JSON.stringify(entities, null, 2)], {{
                        type: "application/json"
                    }});

                    const url = URL.createObjectURL(blob);
                    const a = document.createElement("a");
                    a.href = url;
                    a.download = `annotations_${{textId}}_${{new Date().toISOString().slice(0, 19).replace(/:/g, "-")}}.json`;
                    document.body.appendChild(a);
                    a.click();
                    document.body.removeChild(a);
                    URL.revokeObjectURL(url);
                }};

                updateDisplay();
            }}

            // Function to show a specific text
            function showText(index) {{
                // Hide all annotators
                for (let i = 0; i < texts.length; i++) {{
                    const annotator = document.getElementById(`annotator_${{sessionId}}_${{i}}`);
                    if (annotator) {{
                        annotator.style.display = 'none';
                    }}
                }}

                // Create the annotator if it doesn't exist
                const textId = sessionId + '_' + index;
                let annotator = document.getElementById(`annotator_${{textId}}`);
                if (!annotator) {{
                    textsContainer.insertAdjacentHTML('beforeend', createAnnotatorHTML(texts[index], index));
                    initializeAnnotator(index);
                    annotator = document.getElementById(`annotator_${{textId}}`);
                }}

                // Show the current annotator
                annotator.style.display = 'block';

                // Update counter and buttons
                textCounter.textContent = `Text ${{index + 1}} of ${{texts.length}}`;
                btnPrev.disabled = index === 0;
                btnNext.disabled = index === texts.length - 1;
                btnPrev.style.opacity = index === 0 ? '0.5' : '1';
                btnNext.style.opacity = index === texts.length - 1 ? '0.5' : '1';

                currentIndex = index;
            }}

            // Event listeners for navigation
            btnPrev.onclick = function() {{
                if (currentIndex > 0) {{
                    showText(currentIndex - 1);
                }}
            }};

            btnNext.onclick = function() {{
                if (currentIndex < texts.length - 1) {{
                    showText(currentIndex + 1);
                }}
            }};

            // Button to copy all annotations to clipboard
            document.getElementById("btnCopyAll_" + sessionId).onclick = function() {{
                const allAnnotations = [];

                for (let i = 0; i < texts.length; i++) {{
                    const textId = sessionId + '_' + i;
                    const storageKey = 'ner_' + textId;
                    try {{
                        const stored = localStorage.getItem(storageKey);
                        if (stored) {{
                            const entities = JSON.parse(stored);
                            if (entities.length > 0) {{
                                allAnnotations.push({{
                                    text_id: textId,
                                    text_index: i,
                                    original_text: texts[i],
                                    entities: entities
                                }});
                            }}
                        }}
                    }} catch (e) {{
                        console.warn("Error processing annotation for text", i, e);
                    }}
                }}

                if (allAnnotations.length === 0) {{
                    alert("No annotations found.");
                    return;
                }}

                // Convert annotations to formatted JSON
                const jsonData = JSON.stringify(allAnnotations, null, 2);

                // Copy to clipboard
                navigator.clipboard.writeText(jsonData).then(function() {{
                    // Success - show visual feedback
                    const button = document.getElementById("btnCopyAll_" + sessionId);
                    const originalText = button.textContent;
                    button.textContent = "Copied!";
                    button.style.backgroundColor = "#28a745";
                    
                    // Restore original text after 2 seconds
                    setTimeout(function() {{
                        button.textContent = originalText;
                        button.style.backgroundColor = "#17a2b8";
                    }}, 2000);
                }}).catch(function(err) {{
                    // Fallback for older browsers
                    console.warn("Error copying with navigator.clipboard, trying alternative method:", err);
                    
                    // Alternative method using temporary textarea
                    const textarea = document.createElement('textarea');
                    textarea.value = jsonData;
                    textarea.style.position = 'fixed';
                    textarea.style.opacity = '0';
                    document.body.appendChild(textarea);
                    textarea.select();
                    
                    try {{
                        const successful = document.execCommand('copy');
                        if (successful) {{
                            alert("Annotations copied to clipboard!");
                        }} else {{
                            alert("Error copying annotations.");
                        }}
                    }} catch (err) {{
                        alert("Error copying annotations: " + err);
                    }}
                    
                    document.body.removeChild(textarea);
                }});
            }};

            // Download all annotations
            document.getElementById("btnDownloadAll_" + sessionId).onclick = function() {{
                const allAnnotations = [];

                for (let i = 0; i < texts.length; i++) {{
                    const textId = sessionId + '_' + i;
                    const storageKey = 'ner_' + textId;
                    try {{
                        const stored = localStorage.getItem(storageKey);
                        if (stored) {{
                            const entities = JSON.parse(stored);
                            if (entities.length > 0) {{
                                allAnnotations.push({{
                                    text_id: textId,
                                    text_index: i,
                                    original_text: texts[i],
                                    entities: entities
                                }});
                            }}
                        }}
                    }} catch (e) {{
                        console.warn("Error processing annotation for text", i, e);
                    }}
                }}

                if (allAnnotations.length === 0) {{
                    alert("No annotations found.");
                    return;
                }}

                const blob = new Blob([JSON.stringify(allAnnotations, null, 2)], {{
                    type: 'application/json'
                }});
                const url = URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = `all_annotations_${{sessionId}}_${{new Date().toISOString().slice(0, 19).replace(/:/g, "-")}}.json`;
                document.body.appendChild(a);
                a.click();
                document.body.removeChild(a);
                URL.revokeObjectURL(url);
            }};

            // Initialize by showing the first text
            showText(0);
        }})();
        </script>
        """
        
        display(HTML(main_html + js_code))

