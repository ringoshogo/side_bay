

    function addLotteryForm2() {
        let dateForm2 = document.getElementById( 'dateForm2' );
        dateForm2.classList.add( 'is-show' );
    
    }
    
    function removeLotteryForm2() {
        let dateForm2 = document.getElementById( 'dateForm2' );
        let dateForm3 = document.getElementById( 'dateForm3' );
        if ( dateForm3.className === 'is-show' ) {
            return;
        } else {
            dateForm2.classList.remove( 'is-show' );
        }
    }
    
    function addLotteryForm3() {
        let dateForm3 = document.getElementById( 'dateForm3' );
        dateForm3.classList.add( 'is-show' );
    }
    
    function removeLotteryForm3() {
        let dateForm3 = document.getElementById( 'dateForm3' );
        dateForm3.classList.remove( 'is-show' );
    }

