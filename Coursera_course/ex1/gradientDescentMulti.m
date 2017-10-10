function [theta, J_history] = gradientDescentMulti(X, y, theta, alpha, num_iters)
%GRADIENTDESCENTMULTI Performs gradient descent to learn theta
%   theta = GRADIENTDESCENTMULTI(x, y, theta, alpha, num_iters) updates theta by
%   taking num_iters gradient steps with learning rate alpha

% Initialize some useful values
m = length(y); % number of training examples
J_history = zeros(num_iters, 1);

for iter = 1:num_iters,

    % ====================== YOUR CODE HERE ======================
    % Instructions: Perform a single gradient step on the parameter vector
    %               theta. 
    %
    
    %fprintf('X %f', X)
    %fprintf('x1 %.2f', x1)
    %fprintf('x2 %.2f', x2)
    y_hat = theta(1) 
    for i = 2:size(X, 2),
      y_hat += theta(i) * X(:, i);
    endfor
    theta(1) = theta(1) - alpha * (1/m) * sum(y_hat - y);
    for i = 2:size(X, 2),
      theta(i) -= alpha * (1/m) * sum((y_hat - y) .* X(:, i));
    endfor
    % ============================================================

    % Save the cost J in every iteration    
    J_history(iter) = computeCostMulti(X, y, theta);

end
