
function QOLTotal() {

    let qol_input_fields = document.querySelectorAll(".qol_score:checked");
    let qol_total = 0;

    for (let i = 0; i < qol_input_fields.length; ++i) {
        qol_total += parseInt(qol_input_fields[i].value);
    }
  
    document.querySelector("#qol_score").value = qol_total;
}


function QMGTotal() {

    let qmg_input_fields = document.querySelectorAll(".qmg_score:checked");
    let qmg_total = 0;

    for (let i = 0; i < qmg_input_fields.length; ++i) {
        qmg_total += parseInt(qmg_input_fields[i].value);
    }

    document.querySelector("#qmg_score").value = qmg_total;
}

function MGCompositeTotal() {

    let mg_composite_input_fields = document.querySelectorAll(".mg_composite_score:checked");
    let mg_composite_total = 0;

    for (let i = 0; i < mg_composite_input_fields.length; ++i) {
        mg_composite_total += parseInt(mg_composite_input_fields[i].value);
    }

    document.querySelector("#mg_composite_score").value = mg_composite_total;
}


function ADLTotal() {

    let adl_input_fields = document.querySelectorAll(".adl_score:checked");
    let adl_total = 0;

    for (let i = 0; i < adl_input_fields.length; ++i) {
        adl_total += parseInt(adl_input_fields[i].value);
    }

    document.querySelector("#adl_score").value = adl_total;
}
