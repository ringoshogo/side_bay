var globalCalendar;

function closeArea(){
  $('#detail-area').hide();
}

function getYYYYMM() {
    return globalCalendar.currentDate.format("YYYYMM");
}

function titleTypeChange() {
    var titleType = document.getElementById("title-type");
    var clalenderType =  document.getElementById("calender-type").value;
    if (clalenderType == 0) {
        // モーダルだし分け
        // 抽選フォーム
        titleType.textContent = "抽選エントリーフォーム"; 
      } else {
        titleType.textContent = "予約・二次予約フォーム";
      } 
  }

  function confModalOpen() {
    var clalenderType =  document.getElementById("calender-type").value;
    if (clalenderType == 0) {
      // 抽選エントリー画面
      if (!validationCheck()) {
        errorAlertStr = errorAlert.join(",");
        for (var i = 0; i < errorAlert.length + 1; i++ ) {
          errorAlertMsg = errorAlertStr.replace(",", "");
        }
        alert(errorAlertMsg);
        return;
      }
    } else {
      if (!validationCheck2()) {
        errorAlertStr = errorAlert.join(',');
        for (var i = 0; i < errorAlert.length; i++ ) {
          errorAlertMsg = errorAlertStr.replace(",", "");
        }
        alert(errorAlertMsg);
        return;
      }
    } 

    if (clalenderType == 0) {
      value_conf();
    } else {
      value_conf2();
    }
    $("#calendarModal3").modal(); // モーダル着火
    $("#calendarModal").modal('hide'); // クローズ
    $("#calendarModal2").modal('hide'); // クローズ
  }

  function backForm() {
    var clalenderType =  document.getElementById("calender-type").value;
    if (clalenderType == 0) {
      // モーダルだし分け
      $("#calendarModal3").modal('hide'); // クローズ
      $("#calendarModal").modal(); // モーダル着火
    } else {
      $("#calendarModal3").modal('hide'); // クローズ
      $("#calendarModal2").modal(); // モーダル着火
    }  
  }

  // modalのキャッシュの削除


  // バリデーションチェック
  function validationCheck() {
    var res_num_ =  document.getElementById("res_num").value;
    var res_room =  document.getElementById("res_room").value;
    var res_usage =  document.getElementById("res_usage").value;
    var datepicker_start =  document.getElementById("datepicker_start").value;
    // datepicker_start = trim(datepicker_start);

    errorAlert = [];

    // 配列バージョン
    
    if (res_num_ === '') {
      errorAlert.push("人数の入力がありません" + "\n");
    }
    if (res_room == 0) {
      errorAlert.push("希望の部屋が選択されていません。" + "\n");
    }
    if (res_usage == 0) {
      errorAlert.push("利用形態が選択されていません。" + "\n");
    }
    if (datepicker_start === '') {
      errorAlert.push("予約日の入力がありません" + "\n");
    }
    if (errorAlert.length > 0) {
      return false;
    }
    return true;
  }

  function validationCheck2() {
    var res_num_ =  document.getElementById("res_num2").value;
    var res_room =  document.getElementById("res_room2").value;
    var res_usage =  document.getElementById("res_usage2").value;
    var datepicker_start =  document.getElementById("datepicker_start2").value;
    // datepicker_start = trim(datepicker_start);

    errorAlert = [];

    // 配列バージョン
    
    if (res_num_ === '') {
      errorAlert.push("人数の入力がありません" + "\n");
    }
    if (res_room == 0) {
      errorAlert.push("希望の部屋が選択されていません。" + "\n");
    }
    if (res_usage == 0) {
      errorAlert.push("利用形態が選択されていません。" + "\n");
    }
    if (datepicker_start === '') {
      errorAlert.push("予約日の入力がありません" + "\n");
    }
    if (errorAlert.length > 0) {
      return false;
    }
    return true;
  }

  // 確認画面への値渡し
  function value_conf() {
    var res_num_value =  document.getElementById("res_num").value;
    var res_room_value =  document.getElementById("res_room").value;
    var res_usage_value =  document.getElementById("res_usage").value;
    var datepicker_start_value =  document.getElementById("datepicker_start").value;
    var free_textArea_value =  document.getElementById("free_textArea").value;
    
    var num_conf_value = document.getElementById("num_conf");
    var room_conf_value = document.getElementById("room_conf");
    var usage_conf_value = document.getElementById("usage_conf");
    var day_conf_value = document.getElementById("day_conf");
    var free_text_value = document.getElementById("free_text");


    num_conf_value.innerHTML = res_num_value;
    room_conf_value.innerHTML = res_room_value;
    usage_conf_value.innerHTML = res_usage_value;
    day_conf_value.innerHTML = datepicker_start_value;
    free_text_value.innerHTML = free_textArea_value;

  }

  function value_conf2() {
    var res_num_value =  document.getElementById("res_num2").value;
    var res_room_value =  document.getElementById("res_room2").value;
    var res_usage_value =  document.getElementById("res_usage2").value;
    var datepicker_start_value2 =  document.getElementById("datepicker_start2").value;
    var free_textArea_value =  document.getElementById("free_textArea2").value;
    
    var num_conf_value = document.getElementById("num_conf");
    var room_conf_value = document.getElementById("room_conf");
    var usage_conf_value = document.getElementById("usage_conf");
    var day_conf_value = document.getElementById("day_conf");
    var free_text_value = document.getElementById("free_text");


    num_conf_value.innerHTML = res_num_value;
    room_conf_value.innerHTML = res_room_value;
    usage_conf_value.innerHTML = res_usage_value;
    day_conf_value.innerHTML = datepicker_start_value2;
    free_text_value.innerHTML = free_textArea_value;

  }


calendarInit = function() {

  // 数か月先をとるプロトタイプ　ネットに落ちてた。
  // http://www.is-p.cc/web-skill/javascript-%E4%B8%80%E3%83%B6%E6%9C%88%E5%BE%8C%EF%BC%88n%E3%83%B5%E6%9C%88%E5%BE%8C%EF%BC%89%E3%82%92%E5%8F%96%E5%BE%97%E3%81%99%E3%82%8B%E9%96%A2%E6%95%B0/1159
  Date.prototype.addMonth = function( m ) {
    var d = new Date( this );
    var dates = d.getDate();
    var years = Math.floor( m / 12 );
    var months = m - ( years * 12 );
    if( years ) d.setFullYear( d.getFullYear() + years );
    if( months ) d.setMonth( d.getMonth() + months );
    if( dates == 1 ) {
        d.setDate( 0 );
    } else {
        d.setDate( d.getDate() - 1 );
    }
    return d;
}
  //eventデータ
  var title = "hogeddd";
  var dt = new Date();
  // addMonth関数を使う
  var prem = dt.addMonth( 0 );
  var y = dt.getFullYear();
  var m = ("00" + (dt.getMonth() + 1)).slice(-2);
  var d = ("00" + dt.getDate()).slice(-2);
  i = parseInt(d);
  var nowDate = [];
  for (i = 1; i < 32; i++) {
    nowDate = y + "-" + m + "-" + i;
    console.log(nowDate);
  }

   calendarEvent = {
        url: 'get_all_res_info',
        type: 'GET',
        data: function(){return {yyyymm: getYYYYMM()};},
        success: function(data) {
            console.log("===================================================================================================================");
            console.log(JSON.stringify(data));
        },
        error: function() {
        $('#scrpit-warning').show;
        }
    };

  // カレンダーの設定
  $("#calendar").fullCalendar({
    // new Date();
    defaultDate: prem,
    height: 550,
    lang: "ja",
    selectable: true,
    selectHelper: true,
    editable: true,
    eventLimit: true,
    //eventDurationEditable: false,
    selectable: false,
    editable: false,
    success: function(calEvent) {
      $("#calendar").fullCalendar("removeEvents");
      $("#calendar").fullCalendar("addEventSource", calEvent);
    },

    events : calendarEvent,

    eventClick: function(event) {

      var event_data = '<a href="javascript:void(0);" class="close" onclick="return closeArea();">閉じる</a><br>';

      event_data += event.title + '<br><br>\n';
      event_data += '<b>予約者一覧</b><br>\n';
      if (event.user1) {
        event_data += event.user1+ '<br>\n';
      }
      if (event.user2) {
        event_data += event.user2+ '<br>\n';
      }
      if (event.user3) {
        event_data += event.user3+ '<br>\n';
      }
      if (event.user4) {
        event_data += event.user4+ '<br>\n';
      }

				//<div id="detail-area"></div>の中にevent_dataを入れて表示させる
				$('#detail-area').html(event_data).show();
    },
    dayClick: function(date, jsEvent, view) {
      // 編集ボタンと削除ボタン、ついでに閉じるボタンのHTML要素を追加

      var firstLotteryDay = date.format();
      var datepicker_start = document.getElementById("datepicker_start");
      datepicker_start.value = firstLotteryDay;
      var datepicker_end = document.getElementById("datepicker_end");
      datepicker_end.value = $.datepicker.formatDate("yy-mm-dd", new Date(date._d.setDate(date._d.getDate() + 1)));


      var purposeE = document.getElementsByName("purpose");
      if (purposeE[0]) {
        purposeE[0].selectedIndex = 0;
      }

      var numberOfRoomsE = document.getElementsByName("number_of_rooms");
      if (numberOfRoomsE[0]) {
        numberOfRoomsE[0].value = 1;
      }

        $("#calendarModal").modal(); // モーダル着火

    }
  });
};

$(document).ready(calendarInit);