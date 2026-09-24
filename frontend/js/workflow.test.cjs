const {test} = require('node:test');
const assert = require('node:assert/strict');
const {buildWorkflowDiagram: build} = require('./workflow.js');
test('Choice, eventos ordenados y definición inmutable', () => {
    const definition = {StartAt:'A', States:{A:{Type:'Choice',Choices:[{Variable:'$.ok',BooleanEquals:true,Next:'Fin'}],Default:'Error'},Fin:{Type:'Succeed'},Error:{Type:'Fail'}}};
    const before = JSON.stringify(definition);
    const result = build(definition, [{event_order:2,state_name:'A',state_type:'Choice',status:'SUCCEEDED'}, {event_order:1,state_name:'A',state_type:'Choice',status:'RUNNING'}]);
    assert.match(result.source, /Default/); assert.match(result.source, /class n0 SUCCEEDED/);
    assert.equal(JSON.stringify(definition), before);
});
test('Parallel, unión y nombres duplicados', () => {
    const branch = {StartAt:'T',States:{T:{Type:'Task',End:true}}};
    const result = build({StartAt:'P',States:{P:{Type:'Parallel',Branches:[branch,branch],End:true}}}, [{state_name:'T',state_type:'Task',status:'FAILED',event_order:1}]);
    assert.match(result.source, /subgraph/); assert.match(result.source, /Unión/);
    assert.equal(result.warnings.length, 1);
});
test('Wait activo y caracteres no confiables', () => {
    const name = 'x"</script>\nclick x';
    const result = build({StartAt:name,States:{[name]:{Type:'Wait',End:true}}}, [{state_name:name,state_type:'Wait',status:'RUNNING',event_order:1}]);
    assert.match(result.source, /class n0 WAITING/);
    assert.ok(!result.source.includes('</script>'));
    assert.ok(!result.source.includes('\nclick'));
});
test('Los seis estados visuales tienen estilos', () => {
    const result = build({StartAt:'A',States:{A:{Type:'Succeed'}}});
    for (const status of ['PENDING','RUNNING','SUCCEEDED','FAILED','RETRYING','WAITING']) assert.ok(result.source.includes(`classDef ${status} `));
});
