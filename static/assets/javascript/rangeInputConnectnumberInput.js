const rangeInputs = document.querySelectorAll('input[type="range"]')
const numberInput = document.querySelector('input[type="number"]')

function handleInputChange(e) {
    let target = e.target
    if (e.target.type !== 'range') {
        target = document.querySelector('.range')
    }
    const min = target.min
    const max = target.max
    const val = target.value

    target.style.backgroundSize = (val - min) * 100 / (max - min) + '% 100%'
}

rangeInputs.forEach(input => {
    input.addEventListener('input', handleInputChange)
})

numberInput.addEventListener('input', handleInputChange)




//從這開始debug嘗試做出多個range
const test_array =['qol_score', 'qmg_score'];






// test_array.forEach(e =>
//     function calculateTotal() {
//         test_str = '.'+e+':checked';
//         test_str2 = '#'+e;


//         let input_fields = document.querySelectorAll(test_strs);
//         let total = 0;
    
//         for (let i = 0; i < input_fields.length; ++i) {
//             total += parseInt(input_fields[i].value);
//         }
    
//         document.querySelector(test_str2).value = total;
//     }

// )

