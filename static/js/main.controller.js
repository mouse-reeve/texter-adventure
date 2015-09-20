function MainController($scope, Game) {
    $scope.state = 'waiting';
    $scope.games = {};
    Game.startGame('Alice', '15005550006').then(function(turn) {
        $scope.turn = turn;
        $scope.state = 'approve';
        updateHistory('15005550006');
    });

    $scope.approveTurn = function() {
        Game.sendTurn($scope.turn, '15005550006').then(function () {
            updateHistory('15005550006');
        });
        $scope.state = 'respond';
    };

    $scope.sendResponse = function(option) {
        Game.sendResponse(option, $scope.turn).then(function(turn) {
            $scope.turn = turn;
            $scope.state = 'approve';
            updateHistory('15005550006');
        });
    };

    var updateHistory = function(phone) {
        Game.getGames().then(function(data) {
            $scope.games = data;
        });
    };

}
