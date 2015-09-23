function MainController($scope, Game) {
    $scope.state = {};
    $scope.games = {};
    $scope.turn = [];
    $scope.error = [];

    $scope.startNew = {};

    $scope.newGame = function() {
        Game.startNewGame($scope.startNew.name, $scope.startNew.phone).then(function(turn) {
            $scope.state[$scope.startNew.phone] = 'approve';
            $scope.startNew = {};
            updateHistory();
        });
    };

    $scope.approveTurn = function(phone) {
        Game.sendTurn($scope.turn[phone], phone).then(function(response) {
            if ( !('error' in response) ) {
                $scope.error[phone] = false;
            } else {
                $scope.error[phone] = true;
            }
            updateHistory(phone);
        });
        $scope.state[phone] = 'respond';
    };

    $scope.sendResponse = function(option, phone) {
        Game.sendResponse(option, phone).then(function() {
            $scope.state[phone] = 'approve';
            updateHistory(phone);
        });
    };

    $scope.hideGame = function(game) {
        game.show = false;
        Game.hide(game.phone);
    };

    $scope.checkOptionLength = function(turn) {
        var total = turn.prompt.length;
        angular.forEach(turn.options, function(option) {
            total += 'text' in option ? option.text.length : 0;
        });
        return total >= 160 - (3 * 3) ? 'error' : '';
    };

    $scope.smsError = function(phone) {
        return !!$scope.error[phone] ? 'error' : '';
    };

    var updateHistory = function(phone) {
        Game.getGames().then(function(data) {
            $scope.games = data;

            angular.forEach($scope.games, function(game) {
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
