function MainController($scope, Game) {
    $scope.state = 'waiting';
    Game.startGame().then(function(turn) {
        $scope.turn = turn;
        $scope.state = 'approve';
    });

    $scope.approveTurn = function () {
        Game.sendTurn($scope.turn);
        $scope.state = 'respond';
    };

    $scope.sendResponse = function(option) {
        Game.sendResponse(option, $scope.turn).then(function(turn) {
            $scope.turn = turn;
            $scope.state = 'approve';
        });
    };
}
