// Шаблоны
var part_template = $.templates('#partTemplate',
    "   Title: <span id='task-title-{{:id }}'>{{:title }}</span><br>" +
    "   H1: <span id='task-h1-{{:id }}'>{{:h1 }}</span><br>" +
    "   Img: <a href='{{:img }}' id='task-img-{{:id }}'>{{:img }}</a><br>" +
    "   Status: <span id='task-status-{{:id }}'>{{:status['status']}}</span><br>" +
    "   {{if status['progress']}}Download progress: <span id='task-status-{{:id }}'>{{:status['progress']}}%{{/if}}</span>"
);

var uncompleted_task_template = $.templates("#uncompletedTaskTemplate",
    "   <div>" +
    "       <b>Url: <a href='{{:url}}'>{{:url}}</a> ({{:id}})</b>" +
    "       {{if celery_id && !completed}}" +
    "           <input type=button class='btn-ajax' id='btn-cancel-task-{{:id}}' value='Остановить' data-url='{{:cancel_url}}'>" +
    "       {{/if}}" +
    "   </div>" +
    "   <div id='task-part-{{:id}}'>{{include tmpl='#partTemplate'/}}</div>" +
    "   <div id='progress-{{:id }}' class='progress_bar'></div><br>"
);

var completed_task_template = $.templates("#completedTaskTemplate",
    "       <b>Url: <a href='{{:url}}'>{{:url}}</a> ({{:id}})</b><br>" +
    "       Title: <span id='task-title-{{:id }}'>{{:title }}</span><br>" +
    "       H1: <span id='task-h1-{{:id }}'>{{:h1 }}</span><br>"
);

var task_template = $.templates('#taskTemplate',
    "   {{if finished}}" +
    "       {{include tmpl='#completedTaskTemplate'/}}" +
    "   {{else}}" +
    "       {{include tmpl='#uncompletedTaskTemplate'/}}" +
    "   {{/if}}"
);

var tasks_template = $.templates(
    "   {{for results}}" +
    "       <div id='task-{{:id}}' class='task {{if completed}}completed{{/if}}' data-task-id='{{:id}}'" +
    "               {{if image}} style=\"background:url('{{:image}}') no-repeat left top\"{{/if}}>" +
    "           {{include tmpl='#taskTemplate'/}}" +
    "       </div>" +
    "   {{/for}}"
);

var paginator_template = $.templates(
    "    <div class='pagination'>" +
    "        <span class='step-links'>" +
    "            {{if previous}}" +
    "                <input type=button onClick='get_list(\"{{:previous}}\")' value='&lt;&lt; Prev '>" +
    "            {{/if}}" +

    "            <span class='current'>" +
    "                Page {{:page}} of {{:pages}}" +
    "            </span>" +

    "            {{if next}}" +
    "                <input type=button onClick='get_list(\"{{:next}}\")' value='Next &gt;&gt;'>" +
    "            {{/if}}" +
    "        </span>" +
    "    </div>"
);