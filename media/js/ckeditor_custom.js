CKEDITOR.replace('id_content', {
            toolbar : [
                        ['Source', 
                        '-', 
                        'Bold', 'Italic', 'Underline', 
                        '-', 
                        'Cut','Copy','Paste','PasteText','PasteFromWord', 
                        '-', 
                        'Undo', 'Redo', 
                        '-', 
                        'NumberedList','BulletedList', 'Table', 
                        '-', 
                        'Link', 'Unlink', 'Image', 
                        '-', 
                        'JustifyLeft', 'JustifyCenter', 'JustifyRight', 'JustifyBlock', 
                        '-', 
                        'HorizontalRule']
                    ],
            width: 800,
            height: 400
});

$("#id_content").before('<br /><br />');

