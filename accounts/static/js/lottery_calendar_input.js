$( function () {
    // 本日 + (その月の日数-今日の日付) = ひと月分

    var date = new Date();
    var nowDate = date.getDate();
    console.log( nowDate );
    var nowMonth = date.getMonth() + 1; //今月
    var futMonth = date.getMonth() + 1; //予約可能月　3か月後

    var nowYear = date.getFullYear();
    // 今の月の日数
    var getMonthDays = function ( year, month ) {
        return new Date( year, month, 0 ).getDate();
    };
    var getMonthDay = parseInt( getMonthDays( nowYear, nowMonth ) );
    console.log( getMonthDay );
    //未来の月の日数

    var getFutMonthDay = parseInt( getMonthDays( nowYear, futMonth ) );
    console.log( getFutMonthDay );
    $( "#datepicker_start" ).datepicker( {
        minDate: new Date(),
        //maxDate: ( getFutMonthDay - nowDate ) + "D" + "+3M",
        dateFormat: 'yy-mm-dd',
        showAnim: 'slideDown',
    } );
    $( "#datepicker_end" ).datepicker( {
        minDate: new Date(),
        //maxDate: ( getFutMonthDay - nowDate ) + "D" + "+3M",
        dateFormat: 'yy-mm-dd',
        showAnim: 'slideDown',
    } );
    // $( "#datepicker_end" ).datepicker( {
    //     minDate: ( ( getMonthDay + 1 ) - nowDate ) + "+2M", maxDate: ( getFutMonthDay - nowDate ) + "D" + "+3M",
    //     dateFormat:'yy-mm-dd',
    //     showAnim: 'slideDown',
    // } );
    // $( "#datepicker1" ).datepicker( {
    //     minDate: -23, maxDate: "6D",
    //     dateFormat: 'yy-mm-dd',
    //     showAnim: 'slideDown',
    // } );
    // $( "#datepicker2" ).datepicker( {
    //     minDate: -23, maxDate: "+1M +10D",
    //     dateFormat:'yy-mm-dd',
    //     showAnim: 'slideDown',
    // } );
    
} );


