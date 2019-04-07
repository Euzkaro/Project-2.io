var woeids = [] ;
var current ;
var flag = 'N';

var data = trendStaticData ;

var i;
var j;

for (i = 0; i < trendStaticData.length; i++) { 
    current = trendStaticData[i].woeid;
    flag = 'N' ;
    for (j = 0; j <woeids.length; i++) {
        if (woeids[j] === current) {
            flag = 'Y' ;
        }      
    woeids.push(current);
    }
}
console.log(woeids);