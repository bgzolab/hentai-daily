const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-te-toggle="tooltip"]'));
tooltipTriggerList.map((tooltipTriggerEl) => new te.Tooltip(tooltipTriggerEl));
// hover to show, via: https://tailwind-elements.com/docs/standard/components/tooltip/

const datesAreOnSameDay = (first, second) =>
    first.getFullYear() === second.getFullYear() &&
    first.getMonth() === second.getMonth() &&
    first.getDate() === second.getDate();
const birthday = new Date("2023", "05", "13");

function openAllDetails(){
    // Toggle open all details elements, onload
    // Regardless of their initial status
    document.body.querySelectorAll('details')
    .forEach((e) => {(e.hasAttribute('open')) ?
        e.removeAttribute('open') : e.setAttribute('open',true);
        console.log(e.hasAttribute('open'))
    })
}

function getCurrentPageDate(){
    var url = window.location.href;
    var post_reg = /(http|https):\/\/(.*?)\/(.*?)\/(.*?)\/(.*?).html/i 
    //FIXME: var index_reg = /^((?!-))(xn--)?[a-z0-9][a-z0-9-_]{0,61}[a-z0-9]{0,1}\.(xn--)?([a-z0-9\-]{1,61}|[a-z0-9-]{1,30}\.[a-z]{2,})$/i 
    
    if( post_reg.test(url) ){
        var year = RegExp.$3
        var month = RegExp.$4
        var day = RegExp.$5
        console.log("Current page is at post, so here we go.")
    }else {
        // if ( index_reg.test(url) )
        console.log("Current page is at index, so peace is that, right?")
        return new Date();
    }
    return new Date(year, month-1, day)
}


function time_control(interval) {
    var currentDate = getCurrentPageDate();
    var targetDate = currentDate;
    var today = new Date();
    targetDate.setDate(targetDate.getDate() + interval);
    
    if( targetDate.getTime() < birthday.getTime() ){
        console.log(targetDate + targetDate.getTime() )
        console.log(birthday + birthday.getTime()  )
        // console.log(targetDate < birthday )
        alert("I'm sorry, I don't have page yestoday! 😭");
        return;
    }
    if( targetDate.getTime()  > today.getTime() ){
        console.log(targetDate + targetDate.getTime() )
        console.log(today + today.getTime()  )
        alert("Cherish the moment! ✨");
        return;
    }

    var targetUrl = "/" + targetDate.toLocaleDateString("en-GB").split('/').reverse().join('/') + ".html";
    window.location.href = targetUrl;
}
