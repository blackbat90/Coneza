const assert = require('node:assert/strict');
const {annotate} = require('../backend/static/pcu-draft-editor.js');
const original = {status:'DRAFT', deployable:false, fields:[
    {key:'power', value:null, status:'conflict', sources:[{value:75},{value:100}]},
    {key:'meter', value:null, status:'missing', sources:[]}
]};
const before = JSON.stringify(original);
let edited = annotate(original,'power',' 75 ',' Herstellerdaten prüfen ');
assert.equal(JSON.stringify(original),before);
assert.deepEqual(edited.fields,original.fields);
assert.deepEqual(edited.manual_overrides[0],{key:'power',value:'75',note:'Herstellerdaten prüfen',origin:'manual',status:'unreviewed'});
edited = annotate(edited,'meter','PAC4200','Typenschild');
edited = annotate(edited,'power','100','Korrigiert');
assert.equal(edited.manual_overrides.length,2);
assert.equal(edited.manual_overrides.find(x=>x.key==='power').value,'100');
edited = annotate(edited,'power','','');
assert.equal(edited.manual_overrides.length,1);
assert.equal(edited.manual_overrides[0].key,'meter');
assert.equal(edited.deployable,false);
assert.throws(()=>annotate(original,'unknown','1',''));
assert.throws(()=>annotate(original,'power',75,''));
assert.throws(()=>annotate(original,'power','x'.repeat(2001),''));
assert.equal(annotate({...original,status:'APPROVED',deployable:true},'power','1','').deployable,false);
console.log('Draft editing: evidence preservation, replacement, clearing, validation and unreviewed export passed');
const {restore} = require('../backend/static/pcu-draft-editor.js');
const exported = {status:'APPROVED',deployable:true,configuration_id:'must-not-transfer',
    documents:[{type:'SLD',filename:'sld.pdf'}],
    fields:[{key:'power',label:'Leistung',unit:'kW',value:75,status:'unreviewed',
        sources:[{value:75,document:'sld.pdf',document_type:'SLD',page:1}]}],
    manual_overrides:[{key:'power',value:'100',note:'Typenschild',status:'approved'}]};
const restored = restore(JSON.stringify(exported));
assert.deepEqual(restored.fields,exported.fields);
assert.deepEqual(restored.documents,exported.documents);
assert.equal(restored.status,'DRAFT');
assert.equal(restored.deployable,false);
assert.equal(restored.configuration_id,undefined);
assert.equal(restored.manual_overrides[0].status,'unreviewed');
assert.equal(restored.manual_overrides[0].value,'100');
assert.throws(()=>restore('{'));
assert.throws(()=>restore('x'.repeat(1024*1024+1)));
assert.throws(()=>restore(JSON.stringify({...exported,fields:[exported.fields[0],exported.fields[0]]})));
assert.throws(()=>restore(JSON.stringify({...exported,manual_overrides:[{key:'unknown',value:'1',note:''}]})));
assert.throws(()=>restore(JSON.stringify({...exported,fields:[{...exported.fields[0],sources:[{}]}]})));
console.log('Draft restore: evidence and annotations retained, approval stripped, invalid imports rejected');
