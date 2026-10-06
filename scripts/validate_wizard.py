import sys, io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

with open('backend/templates/index.html', 'r', encoding='utf-8') as f:
    text = f.read()

required_ids = [
    "plantQuestionnaireModal", "plantQuestionnaireForm",
    "wizardNode1", "wizardNode2", "wizardNode3", "wizardNode4", "wizardNode5",
    "wizardStep1", "wizardStep2", "wizardStep3", "wizardStep4", "wizardStep5",
    "questPlantName", "questGridOperatorSelect", "questVoltageSelect", "questPavKw",
    "questHasTrafo", "questTrafoSelect", "questTrafoCustomFields",
    "questComponentsContainer",
    "questMeterSelect", "questProtSelect", "questReactiveMode", "questTargetDeviceSelect",
    "wizardSummaryContent", "btnWizardPrev", "btnWizardNext", "btnSubmitQuestionnaire",
    "questKpiPinst", "questKpiSinst", "questKpiBess", "questKpiTrafoLoad",
    "questSldSvgContainer", "sldFullscreenModal"
]

missing = []
for req_id in required_ids:
    if f'id="{req_id}"' not in text:
        missing.append(req_id)

if missing:
    print("MISSING IDs:", missing)
else:
    print(f"All {len(required_ids)} required IDs present and confirmed!")

# Check JavaScript function definitions
funcs = [
    "updateWizardStepperUI", "validateWizardStep", "goToWizardStep",
    "wizardNextStep", "wizardPrevStep", "updateWizardSummary",
    "openPlantQuestionnaireModal", "openCreatePlantModal"
]
missing_funcs = [fn for fn in funcs if f"function {fn}" not in text]
if missing_funcs:
    print("MISSING FUNCS:", missing_funcs)
else:
    print(f"All {len(funcs)} JavaScript functions present!")
