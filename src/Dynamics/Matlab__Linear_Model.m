%% Fixed Simulation Problem
clear all, close all, clc

% Constants
g = 9.81; % Gravity constant

% Box dimensions
t1 = 0.2; % height of box 1 (m)
l1 = 0.35; % lenght of box 1 (m)
w1 = 0.2; % widht of box 1 (m)

t2 = 0.12; % height of box 2 (m)
l2 = 0.2; % lenght of box 2 (m)
w2 = 0.15; % widht of box 2 (m)

% IT SHOULD BE ON f(x)
l3o = 0.3; % Initial linear actuator lenght (m)
l3f = l3o + 0.3; % Max lenght of linear actuator (m)
l2x = (l1 + l2)/2 + l3f + l3o; % Min distance from rotation to c.g box 2(m)

m1 = 4.5;   % Mass of box 1 (big box) (kg)
m2 = 2.5;   % Mass of box 2 (little box) (kg)
m3 = 0; % Mass of the stick (kg) --> Distributed in m1 and m2

% Rotational Friction (viscosity)
Br = 20; % Rotational Friction constant

% Parameters needed:

% Variables to control
theta = 0; % Angle to stabilize the system ---------
Fc = 1; % Force applied by servomotor --------

% Hipotenuse of the big box
hip = sqrt((t1/2)^2+(l1/2)^2); % hypotenuse for box 1

% Angles needed to calculate the distance 
% for momentum generated by Fcx and Fcy:
beta = asin((t1/2)/hip); % constant 
phi = theta - beta;                        

% Distances needed to calculate the 
% momentum generated by Fcx and Fcy:
ay = sin(phi) * hip;
bx = cos(phi) * hip;

% System Forces:
% Fc (Servo force) decomposition
Fcx = Fc *sin(theta); % x component of servomotor force
Fcy = Fc *cos(theta); % y component of servomotor force

% Gravity forces
F1 = -m1 * g;
F2 = -m2 * g;
F3 = -m3 * g;

% INERTIA

%     % Centroid of the 2 bodies (at initial point)
%     % Define coordinates of both masses
% x1 = [-l1/2        -l1/2        l1/2         l1/2];
% y1 = [-t1/2         t1/2        t1/2        -t1/2];
% x2 = [l2x-(l2/2) l2x-(l2/2) l2x+(l2/2) l2x+(l2/2)];
% y2 = [-t2/2         t2/2        t2/2        -t2/2];
% 
% % Animation in function of the angle
% % R = [cos(phi);-sin(phi);sin(phi);cos(phi)]; % Rotation matrix
% %      % c.g. after rotation by phi
% %   x1 = x1*R; 
% %   x2 = x2*R;
% %   y1 = y1*R; 
% %   y2 = y2*R;
% 
% 
%     % Plot the  system
% polyin = polyshape({x1,x2},{y1,y2}); % plt both shapes
% [x,y] = centroid(polyin); % Calculate centroid of both masses
% plot(polyin)
% hold on
% plot(x,y,'r*')
% [x,y] = centroid(polyin,[1 2]); %plt centroid of system
% plot(polyin)
% hold on
% plot(x(1),y(1),'r*',x(2),y(2),'r*'); %plt centroid for each body
% hold on
% plot([x(1) x(2)], [y(1) y(2)]); % plt line conection between the points
% hold off
% 
%     % Inital C.G.
%  cg1 = [x(1) y(1)]; 
%  cg2 = [x(2) y(2)];
 
    % Inertia for the axis of rotation
 I1 = (m1 * (t1^2 + l1^2))/12; % Rotational inertia of box 1 [Kg*m^2]
 I2 = (m2 * (t2^2 + l2^2))/12 + (m2 * l2x^2) ; % Rotational inertia of box 2 [Kg*m^2]
 
 I = I1 + I2; % Rotational Inertia

% DYNAMICS EQUATIONS:

% X Axis - Force equilibrium
Rx = - Fcx

% Y Axis - Force equilibrium
Ry = F1 + F2 - Fcy

% Mz - Momentum equilibrium
theta_dot_dot = (1/I)*((Fcx*ay) + (Fcy*bx) - (F2*l2x)*cos(theta))

% LINEARIZATION
% small-angle approximations: 
cos_theta_sa = 1; %cos_theta_sa = (1-(theta^2/2));
sin_theta_sa = theta;

linear_ay = (sin_theta_sa*cos(beta) - cos_theta_sa*sin(beta))*hip;
linear_bx = (cos_theta_sa*cos(beta) + sin_theta_sa*sin(beta))*hip;

Fcx_sa = Fc *sin_theta_sa; % x component of servomotor force
Fcy_sa = Fc *cos_theta_sa; % y component of servomotor force

% Linearized model
theta_dot_dot_approx = (1/I)*((Fcx_sa*linear_ay) + (Fcy_sa*linear_bx) - (F2*l2x)*cos_theta_sa)

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% Simulink Parameters 
M2 = (F2*l2x); % M2 Torque
H = hip * cos(-beta); % u = Fc * H

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% Simple model (l3d does not change => I constant)
% Matrices Definition
A = [0 1 ; 0 Br/I]; % F2*theta*l2x/2I
B = [0 0 ; -H/I -l2x/I];
C = [1 0];

% Check controllability
controllability =['Check Controllability = ',num2str(rank(ctrb(A,B)))];
disp(controllability)

% Number of states 
n = length(A);

% Output matrix
%C = eye(length(A));

% Open loop system
sys_ol = ss(A,B,C,0);

% Simulate open loop system
x0 = [pi/2;0];
figure
initial(sys_ol,x0)


% LQR 1
Q1 = eye(n)*100;
R1 = 2;
K1 = -lqr(A,B,Q1,R1);

% LQR 2
Q2 = eye(n)*100;
R2 = 1;
K2 = -lqr(A,B,Q2,R2);

% Closed loop system
Acl1 = A+B*K1;
Acl2 = A+B*K2;

sys_cl1 = ss(Acl1,zeros(n,1),C,0);
sys_cl2 = ss(Acl2,zeros(n,1),C,0);

figure
initial(sys_cl1,x0)
hold on
initial(sys_cl2,x0)
legend('LQR_1','LQR_2')

















