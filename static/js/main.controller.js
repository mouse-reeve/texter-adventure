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
            $scope.updateHistory();
        });
    };

    $scope.restart = function(game) {
        Game.startNewGame(game.name, game.phone).then(function(turn) {
            $scope.updateHistory();
        });
    };

    $scope.approveTurn = function(phone) {
        $scope.state[phone] = 'waiting';
        Game.sendTurn($scope.turn[phone], phone).then(function(response) {
            if ( !('error' in response) ) {
                $scope.error[phone] = false;
            } else {
                $scope.error[phone] = true;
            }
            $scope.updateHistory(phone);
            $scope.state[phone] = 'respond';
        });
    };

    $scope.sendResponse = function(option, phone) {
        $scope.state[phone] = 'waiting';
        Game.sendResponse(option, phone).then(function() {
            $scope.state[phone] = 'approve';
            $scope.updateHistory(phone);
        });
    };

    $scope.setName = function(game) {
        Game.setName(game.newName, game.phone).then(function() {
            game.name = game.newName;
        });
    };

    $scope.setUID = function(game) {
        Game.setUID(game.newUID, game.phone).then(function() {
            $scope.updateHistory();
        });
    };

    $scope.hideGame = function(game) {
        game.show = false;
        Game.hide(game.phone);
    };

    $scope.removeOptions = function(phone) {
        delete $scope.turn[phone].prompt;
        $scope.turn[phone].options = null;
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

    $scope.updateHistory = function(phone) {
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

    $scope.updateHistory();
}
