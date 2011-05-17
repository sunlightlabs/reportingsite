var iframe = "<iframe src='http://reporting.sunlightfoundation.com/lobbying/registrations/widget?embedder=" + encodeURIComponent(location.href) + "&embedder_host=" + encodeURIComponent(location.host) + "' width='250' height='400' frameborder='0' scrolling='no'></iframe>";

var element = "";
if (element)
  document.getElementById(element).innerHTML = iframe;
else
  document.write(iframe);
