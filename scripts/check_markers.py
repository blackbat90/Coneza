import re

with open('backend/templates/index.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Verify markers
assert 'id="plantQuestionnaireModal"' in content, "Modal not found"
assert 'id="plantQuestionnaireForm"' in content, "Form not found"
assert 'id="questPlantName"' in content, "Step 1 not found"
assert 'id="questTrafoSelect"' in content, "Step 2 not found"
assert 'id="questComponentsContainer"' in content, "Step 3 not found"
assert 'id="questMeterSelect"' in content, "Step 4 not found"
assert 'id="btnSubmitQuestionnaire"' in content, "Submit button not found"

print("All questionnaire markers verified successfully!")
