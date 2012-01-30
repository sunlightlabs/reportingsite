var iframe = '<iframe src="http://{{ host }}/independent-expenditures/widget?embedder=' + encodeURIComponent(location.href) + '&embedder_host=' + encodeURIComponent(location.host) + '" width="350" height="400" frameborder="0"></iframe>';
document.write(iframe);
