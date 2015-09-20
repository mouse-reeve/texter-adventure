function MainController($scope, Game) {
    $scope.state = {};
    $scope.games = {};
    $scope.turn = [];

    $scope.startNew = {};

    $scope.newGame = function () {
        Game.startNewGame($scope.startNew.name, $scope.startNew.phone).then(function(turn) {
            $scope.state[$scope.startNew.phone] = 'approve';
            updateHistory();
        });
    };

    $scope.approveTurn = function(phone) {
        Game.sendTurn($scope.turn[phone], phone).then(function () {
            updateHistory(phone);
        });
        $scope.state[phone] = 'respond';
    };

    $scope.sendResponse = function(option, phone) {
        Game.sendResponse(option, phone).then(function(turn) {
            $scope.state[phone] = 'approve';
            updateHistory(phone);
        });
    };

    var updateHistory = function(phone) {
        Game.getGames().then(function(data) {
            $scope.games = data;

            angular.forEach($scope.games, function (game) {
                if (game.turn_history.length && game.turn_history[game.turn_history.length - 1].type == 'turn') {
                    $scope.state[game.phone] = 'respond';
                } else {
                    $scope.state[game.phone] = 'approve';
                }

                $scope.turn[game.phone] = game.current_turn;
            });
        });
    };

    updateHistory();
}
