$(document).ready(function () {
    get_files("-");
});

var selected_file_list = [];
var file_in_drag = null;
var copy_selected_file_list = [];
var sort_a_z_value = true;

function reset_selected() {

    $('.check-file').each(function (i, obj) {
        $(obj).removeClass('fa-check');
    })

    selected_file_list = [];
    copy_selected_file_list = [];
}

function create_folder() {
    var loc = $('#location').attr("data-location");
    var folder_name = $('#created_folder_name').val();
    data = {"folder_name": folder_name, 'loc': loc};
    $.ajax({
        url: createFolderUrl,
        type: 'POST',
        dataType: 'json',
        data: data,
    });
    $('#collapseCreateFolder').collapse("hide");
    get_files(loc);
}

function sort_a_z(d) {
    loc = $('#location').attr("data-location");
    $(d).toggleClass('fa-sort-alpha-desc');
    if ($(d).attr("data-sort") === "a-z") {
        $(d).attr("data-sort", "z-a");
        sort_a_z_value = false;
    } else {
        $(d).attr("data-sort", "a-z");
        sort_a_z_value = true;
    }
    get_files(loc);
}

function copyToClipboard(element) {
    var $temp = $("<input>");
    let t = $(element).text();
    $(element).parent().append($temp);
    $temp.val(t).select();
    document.execCommand("copy");
    $temp.remove();
}

function get_s3_path(d) {
    let h = "";
    let p = "";

    for (let i in selected_file_list) {
        p = selected_file_list[i].trim().slice(1);
        h += `
                <div>
                    <a href="javascript:;">
                        <span onclick="copyToClipboard(this);">${p}</span>
                    </a>
                </div>
            `
    }
    $('#js-paths-links').html(h);
    $('#modalCenter').modal('show');
}

function select_file(d) {
    $(d).find('.check-file').toggleClass('fa-check');
    $(d).parent().siblings().find('.check-file').removeClass('fa-check');
    var file_item = $(d).find('.location-info').text();
    if (selected_file_list.indexOf(file_item) !== -1) {
        selected_file_list.splice(selected_file_list.indexOf(file_item), 1)
    } else {
        selected_file_list.push(file_item);
    }
}

function copy_selected_file() {
    copy_selected_file_list = selected_file_list;
    $('#paste_file').removeClass('hidden');
    $('#move_file').removeClass('hidden');
}


function paste_file() {
    loc = $('#location').attr("data-location");
    $('#paste_file').toggleClass('hidden');
    $('#move_file').toggleClass('hidden');
    data = {'loc': loc, 'file_list': copy_selected_file_list};
    $.ajax({
        url: pasteFileUrl,
        type: 'POST',
        dataType: 'json',
        data: data,
        success: function (resultData) {
            copy_selected_file_list = [];
            refresh_folder();
        },
    });
}


function delete_file() {
    loc = $('#location').attr("data-location");
    data = {'file_list': selected_file_list};
    $.ajax({
        url: deleteFileUrl,
        type: 'POST',
        dataType: 'json',
        data: data,
        success: function (resultData) {
            refresh_folder();
        },
    });
}


function refresh_folder() {
    get_files($('#location').attr("data-location"));
}

// item detail

function open_item(d) {
    url = d.getAttribute("data-url");
    type = d.getAttribute("data-type");
    if (type === 'folder') {
        get_files("-" + url)
    } else {
        // window.open(url, '_blank');
        edit_item(d);
    }
}


function get_item(d) {
    // open file content in new tab
    let file_item = $(d).find('.location-info').text();
    window.open(getItemUrl + "?file=" + file_item, "_blank");
}

function edit_item(d) {
    let file_item = $(d).find('.location-info').text();

    $.ajax({
        url: getItemContentUrl + "?file=" + file_item,
        type: 'GET',
        dataType: 'json',
        success: function (resultData) {
            $("#js-file-name").text(file_item.trim().substr(1));
            $('#js-editor-text').val(resultData['content']);
            $('#modelCKEditor').modal('show');
        },
        error: function (resultData) {
            alert(resultData.responseJSON['content']);
        }
    });
}

function update_item_text(d) {
    let file_item = '-' + $("#js-file-name").text().trim();
    let content = $("#js-editor-text").val();

    $.ajax({
        url: updateItemContentUrl,
        type: 'POST',
        dataType: 'json',
        data: {
            "file": file_item,
            "content": content
        },
        success: function (resultData) {
            $('#modelCKEditor').modal('hide');
        },
        error: function (resultData) {
            alert(resultData)
        }
    });
}

// back top folder

function back_folder(d) {
    var loc = d.getAttribute('data-top_folder');
    get_files(loc);
    $('#location').attr("data-location", loc);
    var top_loc = "";
    var loc_array = loc.split('/');
    for (var i = 0; i < loc_array.length - 2; i++) {
        top_loc = top_loc + loc_array[i] + "/"
    }
    if (1 > top_loc.length) {
        top_loc = "-"
    }
    $('#top_folder').attr("data-top_folder", top_loc);
}

// "fetch the directories within the selected folder"

function get_files(main_folder) {
    selected_file_list = [];
    $('#top_folder').attr("data-top_folder", $('#location').attr("data-location"));
    $('#location').attr("data-location", main_folder);
    var get_files_url = getFolderItemsUrl.replace(/arg1djs3server/, main_folder.toString()).replace(/sort_a_z/, sort_a_z_value);
    $.getJSON(
        get_files_url, function (files_list) {

            $(".pb-filemng-template-body").empty();

            for (var key in files_list) {
                target = "";
                if ('folder' != files_list[key].type) {
                    target = 'target="_blank"';
                }


                $(".pb-filemng-template-body").append(
                    `
                        <div class="col-sm-2 pb-filemng-body-folders"
                                onClick="select_file(this);"
                                ondblclick="open_item(this);"
                                data-toggle="tooltip"
                                ondrop="drop_file(event)"
                                ondragover="allowDrop_file(event)"
                                ondragstart="dragstart_file(event)"
                                ondragend="dragend_file(event)"

                                draggable="true"
                                title="${files_list[key].text}"
                                data-url="${files_list[key].url}"
                                data-type="${files_list[key].type}">

                            <img src="${files_list[key].icon}"/>

                            <br/>

                            <p class="pb-filemng-paragraphs" onClick="rename_file_onfocus(this);">
                                ${files_list[key].text}
                            </p>

                            <input type="text" class="form-control hidden rename-input"
                                        onfocusout="rename_file_onfocusout(this);"
                                        onkeypress="rename_file_onkeypress(this, event);"
                                        value="${files_list[key].text}">

                            <span class="fa check-file"></span>

                            <span class="hide location-info"> ${main_folder}${files_list[key].text}</span>

                        </div>
                    `
                );
            }
            if (1 > files_list.length) {
                $(".pb-filemng-template-body").append('<p style="text-align:center">folderEmptyText</p>');
            }
        });
}

function download_files() {
    for (var key in selected_file_list) {
        window.open(downloadUrl + "?file=" + selected_file_list[key], "_blank");
    }
}

// rename item focus

function rename_file_onfocus(d) {
    $(d).parent().find('.rename-input').removeClass('hidden');
    $(d).parent().find('.rename-input').focus();
    $(d).removeClass('hidden');
}

// rename item focusout

function rename_file_onfocusout(d) {
    var file = $(d).parent().find('.pb-filemng-paragraphs').html();
    var loc = $('#location').attr("data-location");
    var new_name = $(d).val();
    data = {'loc': loc, 'file': file, 'new_name': new_name};

    if (file.trim() === new_name.trim()) {
        $(d).parent().find('.pb-filemng-paragraphs').removeClass('hidden');
        $(d).addClass('hidden');
        return
    }

    $.ajax({
        url: renameFileUrl,
        type: 'POST',
        dataType: 'json',
        data: data,
        success: function (resultData) {
            $(d).parent().find('.pb-filemng-paragraphs').html(resultData);
            $(d).parent().find('.pb-filemng-paragraphs').removeClass('hidden');
            $(d).addClass('hidden');
        },
        error: function (resultData) {
            $(d).parent().find('.pb-filemng-paragraphs').removeClass('hidden');
            $(d).addClass('hidden');
        }
    });
    refresh_folder();
}

function rename_file_onkeypress(d, e) {
    if (e.keyCode === 13) { //enter
        rename_file_onfocusout(d);
        reset_selected();
    } else if (e.keyCode === 27) { //esc
        $(d).parent().find('.pb-filemng-paragraphs').removeClass('hidden');
        $(d).toggleClass('hidden');
        reset_selected()
    }
}

function move_file(loc, file_list) {
    $('#move_file').toggleClass('hidden');
    $('#paste_file').toggleClass('hidden');
    data = {'loc': loc, 'file_list': file_list};
    $.ajax({
        url: moveFileUrl,
        type: 'POST',
        dataType: 'json',
        data: data,
        success: function (resultData) {
            // get_files($('#location').attr("data-location"));
        },
        error: function (result) {
            //
        }
    });
    refresh_folder();
}


function move_selected_file(d) {
    move_file($('#location').attr("data-location"), copy_selected_file_list);
}


// drag and drop file for move file start


function dragstart_file(e) {
    var file_item = $(e.currentTarget).find('.location-info').text();
    if (selected_file_list.indexOf(file_item) === -1) {
        selected_file_list.push(file_item);
    }
    for (var key in selected_file_list) {
        $("div[title=\"" + selected_file_list[key].slice(1) + "\"]")[0].style.opacity = '0.4';
    }
}

function dragend_file(e) {
    for (var key in selected_file_list) {
        $("div[title=\"" + selected_file_list[key].slice(1) + "\"]")[0].style.opacity = '1';
    }
}

function drop_file(e) {
    e.preventDefault();
    if ($(e.target).parent().attr("data-type") === 'folder') {
        move_file("-" + $(e.target).parent().attr("title"), selected_file_list);
    }
}

function allowDrop_file(e) {
    e.preventDefault();
}

$(function () {
    'use strict';

    // UPLOAD CLASS DEFINITION
    // ======================

    var dropZone = document.getElementById('drop-zone');
    var uploadForm = document.getElementById('js-upload-form');

    var startUpload = function (files) {
        var loc = $('#location').attr("data-location");
        $.each(files, function (key, file) {
            var data = new FormData();
            data.append("file", file);
            data.append("loc", loc);
            $.ajax({
                xhr: function () {
                    var xhr = new window.XMLHttpRequest();
                    // Upload progress
                    xhr.upload.addEventListener("progress", function (evt) {
                        if (evt.lengthComputable) {
                            var percentComplete = (evt.loaded / evt.total * 100 | 0);
                            var progress_bar = document.getElementById("progress-bar");
                            var progress_bar_rate = document.getElementById("progress-bar-rate");
                            progress_bar.style.width = percentComplete + '%';
                            progress_bar_rate.innerHTML = percentComplete + ' % ' + file.name;
                        }
                    }, false);
                    return xhr;
                },
                url: uploadUrl,
                contentType: false,
                type: 'POST',
                dataType: 'json',
                processData: false,
                data: data,
                success: function (resultData) {
                    document.getElementById("js-upload-finished-list").innerHTML +=
                        `
                    <a href="#" class="list-group-item list-group-item-success">
                        <span class="badge alert-success pull-right">${successText}</span>
                        ${file.name}
                    </a>
                    `;
                    $('#collapseUpload').collapse("hide")
                },
                error: function (resultData) {
                    document.getElementById("js-upload-finished-list").innerHTML +=
                        `
                    <a href="#" class="list-group-item list-group-item-danger">
                        <span class="badge alert-danger pull-right">${failText}</span>
                        ${file.name}
                    </a>
                    `;
                }
            });
        });
        get_files(loc);
    };

    uploadForm.addEventListener('submit', function (e) {
        var uploadFiles = document.getElementById('js-upload-files').files;
        e.preventDefault();
        startUpload(uploadFiles);
    });

    dropZone.ondrop = function (e) {
        e.preventDefault();
        this.className = 'upload-drop-zone';
        startUpload(e.dataTransfer.files)
    };

    dropZone.ondragover = function () {
        this.className = 'upload-drop-zone drop';
        return false;
    };

    dropZone.ondragleave = function () {
        this.className = 'upload-drop-zone';
        return false;
    }

});