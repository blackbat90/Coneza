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
