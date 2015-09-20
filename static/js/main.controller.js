function MainController($scope, Game) {
    $scope.state = 'waiting';
    $scope.games = {};

    $scope.newGame = function () {
        Game.startNewGame('Alice', '15005550006').then(function(turn) {
            $scope.turn = turn;
            $scope.state = 'approve';
            updateHistory('15005550006');
        });
    };

    $scope.approveTurn = function(phone) {
        Game.sendTurn($scope.turn, phone).then(function () {
            updateHistory(phone);
        });
        $scope.state = 'respond';
    };

    $scope.sendResponse = function(option, phone) {
        Game.sendResponse(option, $scope.turn).then(function(turn) {
            $scope.turn = turn;
            $scope.state = 'approve';
            updateHistory(phone);
        });
    };

    var updateHistory = function(phone) {
        Game.getGames().then(function(data) {
            $scope.games = data;
        });
    };

    updateHistory();
}
