function output = simulation_history(instance)

persistent init
persistent historian
persistent max_index
persistent history_index


if isempty(init)
max_index = 1000;
historian = create_historian(instance, max_index);
history_index = 1;
historian = record_history(instance, historian, history_index);
init = false;
end

if exist("instance", "var")

history_index = history_index +1;

while instance.t <= historian.t(history_index-1) && history_index > 2
history_index = history_index -1;
end


if history_index >= max_index
max_index     = max_index     +1000;
history_index = history_index +1000;
historian = record_history(instance, historian, history_index);
history_index = history_index -1000;
end

historian = record_history(instance, historian, history_index);

end

if nargout > 0
    flatten(historian.t(1:history_index))
    output = trim_historian(historian, 2:history_index-2);
end


end





   


