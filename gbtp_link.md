list link
- javascript yes/no : yes
- selector : table.board-list tbody tr td:nth-child(2) a
- link pattern : javascript:void(0); onclick="javascript:fn_detail('{ID}','{NUM}')"

pagination link
- javascript yes/no : no
- selector : div.paging a
- link pattern : ?pageIndex={PAGE_NUM}

detail link
- selector : table.board-view

attachment link
- javascript yes/no : yes
- selector : table.board-view td.file-list a
- link pattern : javascript:;