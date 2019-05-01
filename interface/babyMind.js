function draw(){
        var thresholdHG=document.getElementById('threshold_HG').value;
        var thresholdLG=document.getElementById('threshold_LG').value;
        var thresholdDAC=document.getElementById('threshold_DAC').value;
        var gain=document.querySelector('input[name=gain]:checked').value;
        var triggerConf=document.getElementById('confForm').value;
        var averageDAC=document.getElementById('averageDAC').value;
        var triggerChoosen=document.getElementById('triggerChoosenForm').value;
        var thresholdFrom=document.getElementById('thresholdFrom').value;
        var thresholdTo=document.getElementById('thresholdTo').value;
        var LGorHGTemp=document.getElementById('LGorHG');
        var LGorHG=LGorHGTemp.options[LGorHGTemp.selectedIndex].value;
        var step=document.getElementById('step').value;
        // console.log(thresholdHG);//ok
        // console.log(thresholdLG);//ok
        // console.log(thresholdDAC);//ok
        // console.log(gain); //ok
        // console.log(triggerConf); //ok
        // console.log(averageDAC)//ok
        // console.log(triggerChoosen);//ok
        // console.log(thresholdFrom);//ok
        // console.log(thresholdTo);//ok
        // console.log(LGorHG);//ok
        // console.log(step);
}
document.getElementById('drawCoscmicFluxButton').addEventListener("click",draw);
