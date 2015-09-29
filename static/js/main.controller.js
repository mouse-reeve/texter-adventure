function MainController($scope, Game) {
    $scope.state = {};
    $scope.games = {};
    $scope.turn = [];
    $scope.error = [];

    $scope.newGame = function() {
        Game.startNewGame().then(function(turn) {
            $scope.state[$scope.startNew.phone] = 'approve';
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
        Game.update(game.phone, {'name': game.newName}).then(function() {
            game.name = game.newName;
        });
    };

    $scope.setUID = function(game, uid) {
        Game.setUID(uid, game.phone).then(function() {
            $scope.updateHistory();
        });
    };

    $scope.hideGame = function(game) {
        game.show = false;
        Game.update(game.phone, {'show': false});
    };

    $scope.removeOptions = function(phone) {
        delete $scope.turn[phone].prompt;
        delete $scope.turn[phone].options;
    };

    $scope.addOptions = function(phone) {
        $scope.turn[phone].prompt = 'Please select an option:';
        $scope.turn[phone].options = [
            {'text': '', 'pointsTo': null},
            {'text': '', 'pointsTo': null},
            {'text': '', 'pointsTo': null},
            {'text': 'Other', 'pointsTo': null}
        ];
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
            console.log($scope.games);

            angular.forEach($scope.games, function(game) {
                if (game.messages.length && !game.messages[game.messages.length - 1].incoming) {
                    $scope.state[game.phone] = 'respond';
                } else {
                    $scope.state[game.phone] = 'approve';
                }

                $scope.turn[game.phone] = game.pending_turn;
            });
        });
    };

    $scope.updateHistory();
}
