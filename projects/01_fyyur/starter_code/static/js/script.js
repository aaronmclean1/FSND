window.parseISOString = function parseISOString(s) {
  var b = s.split(/\D+/);
  return new Date(Date.UTC(b[0], --b[1], b[2], b[3], b[4], b[5], b[6]));
};

function deleteData(url, item) {
  var r = confirm("Are you sure you want to delete this?");
  if (r == true) {
    return fetch(url + '/' + item, {
      method: 'delete'
    }).then(response =>
      response.json().then(json => {
        if (json.success == true) {
          alert('The item has been deleted. The page will reload now.');
          location.reload();
        }
        return json;
      })
    );
  } else {
    return false;
  }
}

//Jquery datapicker function for shows
$(function() {
	$('#start_time').datepicker({
        dateFormat: 'yy-mm-dd',
        onSelect: function(datetext){
            var d = new Date(); // for now
            var h = d.getHours();
        		h = (h < 10) ? ("0" + h) : h ;

        		var m = d.getMinutes();
            m = (m < 10) ? ("0" + m) : m ;

            var s = d.getSeconds();
            s = (s < 10) ? ("0" + s) : s ;

        		datetext = datetext + " " + h + ":" + m;
            $('#start_time').val(datetext);
        },
    });
});

