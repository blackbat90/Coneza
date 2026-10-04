with open('backend/templates/index.html', 'r', encoding='utf-8') as f:
    text = f.read()

print('index.html size:', len(text), 'chars')
print('Questionnaire occurrences:', text.count('Questionnaire'))
print('Modal plantQuestionnaireModal present:', 'id="plantQuestionnaireModal"' in text)
print('Function openPlantQuestionnaireModal present:', 'function openPlantQuestionnaireModal' in text)
print('Function handlePlantQuestionnaireSubmit present:', 'function handlePlantQuestionnaireSubmit' in text)
