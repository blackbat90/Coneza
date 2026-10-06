import sys, io, re

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

with open('backend/templates/index.html', 'r', encoding='utf-8') as f:
    html = f.read()

print("Original length:", len(html))

# Check modal start and end
modal_start_pattern = r'(<!-- =+ -->\s*<!-- Interaktiver Anlagen-Fragebogen \(SLD-Ersatz\) Modal -->\s*<!-- =+ -->\s*<div class="modal-backdrop" id="plantQuestionnaireModal"[^>]*>)'
match = re.search(modal_start_pattern, html)
assert match, "Could not find modal start"
print("Found modal start at index:", match.start())

# Let's verify existing elements
assert 'id="plantQuestionnaireModal"' in html
assert 'id="plantQuestionnaireForm"' in html
assert 'id="questPlantName"' in html
assert 'id="questTrafoSelect"' in html
assert 'id="questComponentsContainer"' in html
assert 'id="questMeterSelect"' in html
assert 'id="questSldSvgContainer"' in html
assert 'id="btnSubmitQuestionnaire"' in html

print("All elements found and confirmed!")
