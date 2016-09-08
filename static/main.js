// актуальные прогресс-бары
var bars = {};

// cокеты
var socket_pool = {};
var closeAllSockets = function() {
    for (var id in socket_pool) {
        if (!!socket_pool[id])
            socket_pool[id].close();
        socket_pool[id] = false;
    }
};

// функция для запуска колбеков, заданных в атрибутах тегов
function _do(callback, el, args) {
    if (callback) {
        if (typeof(callback) === 'function') {
            callback.call(el, args);
        } else if (callback != undefined && window[callback]) {
            window[callback].call(el, args);
        }
    }
}

// Получениe списка задач
var get_list = function(url) {
    if (!url) {
        var url = django_vars['url'];
    }
    $.ajax({
        url: url,
        success: function(data) {
            // Рендерим теплейт задач
            $('#tasksList').html(tasks_template.render(data));

            // Рендерим теплейт пажинации
            if (data['pages'] > 1) {
                $('.paginator').html(paginator_template.render(data));
                $('.paginator').show();
            } else {
                $('.paginator').hide();
            }

            // Меняем адресную строку браузера, чтобы после F5
            // увидеть правильный page
            history.pushState({}, '', '?page=' + data['page']);
        },
        complete: function(data) {
            // Обнуляем список прогресс-баров и сокетов, т.к. новая
            // страница - список задач новый.
            bars = {};
            closeAllSockets();
            
            // Для каждого блока инициируем получение статуса.
            $('.task').each(function(){
                connect_to_tornado($(this)[0].getAttribute('data-task-id'));
            });

        },

        fail: function(data) {
            $('#tasks-list').html(data);
        }
    });
};

// Обработка соединения с торнадо (оттуда приходят изменения состояний
// задач).
var connect_to_tornado = function(id) {
    if (!id)
        return;

    if (socket_pool[id] && socket_pool[id].readyState != 3)
        return;

    var socket_url = django_vars['tornado_url'];
    socket_pool[id] = new SockJS(socket_url, null, {
        'protocols_whitelist': [
            'websocket', 'xdr-streaming', 'xhr-streaming',
            'iframe-eventsource', 'iframe-htmlfile', 'xdr-polling',
            'xhr-polling', 'iframe-xhr-polling', 'jsonp-polling'
        ],
        // 'debug': true, 'devel': true,
    });

    // Подсоединяемся к серверу
    socket_pool[id].onopen = function(e) {
        // Говорим серверу, что хотим подключиться к задаче id
        socket_pool[id].send(JSON.stringify({
            'type': 'connect',
            'task_id': id,
        }));
    };

    // Пришло сообщение (состояние задачи)
    socket_pool[id].onmessage = function(msg) {
        var data = JSON.parse(msg.data);
        var task_status = data['status']

        // Отображаем изменения.
        $('#task-part-'+id).html(part_template.render(data));

        // Если текущее состояние - закачка картинки,
        // то отображаем прогресс-бар и показываем % выполнения
        if (task_status['status'] == 'DOWNLOAD IMG') {
            if ($('#progress-'+id)[0]) {
                if (!bars[id]) {
                    bars[id] = new Nanobar({
                        target: $('#progress-'+id)[0],
                    });
                }
                bars[id].go(task_status['progress']);
            }
        }

        // Если пришел один из этих статусов, то закрываем соединение
        // за ненадобностью
        if (task_status['status'] == 'Completed!' 
                || task_status['status'] == 'Broken!'
                || task_status['status'] == 'REVOKED'
                || task_status['status'] == 'FAILURE'
                || task_status['status'] == 'SUCCESS') {
            socket_pool[id].close();
            if (task_status['status'] == 'Completed!') {
                $('#task-'+id).html(task_template.render(data));
                if (data['image'] && $('#task-'+id).css('background').indexOf(data['image']) == -1) {
                    $('#task-'+id).css('background', "url('" + data['image'] + "') no-repeat");
                }
            }
        }
    };

    socket_pool[id].onclose = function(event) {
        if (event.wasClean)
            return;
        // при потере соединения, переподключаемся
        setTimeout(function() {
            connect_to_tornado(id);
        }, 1000);
    };
};


$(document).ready(function() {
    // Помогает быстро создавать аякс-контролы
    $('body').on('click', '.btn-ajax', function() {
        var callback = $(this).attr('data-callback');
        $.ajax({
            type: 'POST',
            url: $(this).attr('data-url'),
            complete: function(data) {
                if (callback) {
                    _do(callback);
                }
            }
        });     
        return false;        
    })
    // При первой загрузке окна инициируем загрузку списка блоков. 
    get_list(django_vars['url']);

    // $('#create-form').submit(function() {
    //     $.ajax({
    //         data: $(this).serialize(),
    //         type: $(this).attr('method'),
    //         url: $(this).attr('action'),
    //         success: function(response) {
    //             $('#tasks-list').html(response);
    //         }
    //     });
    //     return false;
    // });

});
