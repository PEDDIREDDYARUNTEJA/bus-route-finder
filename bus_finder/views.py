from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from .models import Stop, Bus, BusStop
from .forms import BusForm, StopForm

def home(request):
    """
    Renders main route finder page with source & destination dropdowns populated from DB.
    Also handles GET search parameters if submitted directly.
    """
    stops = Stop.objects.all().order_by('name')
    
    source_id = request.GET.get('source')
    dest_id = request.GET.get('destination')
    
    selected_source = None
    selected_dest = None
    results = []
    searched = False

    if source_id and dest_id:
        searched = True
        try:
            source_id = int(source_id)
            dest_id = int(dest_id)
            selected_source = Stop.objects.filter(id=source_id).first()
            selected_dest = Stop.objects.filter(id=dest_id).first()
            
            if selected_source and selected_dest and source_id != dest_id:
                results = get_matching_buses(source_id, dest_id)
        except (ValueError, TypeError):
            pass

    context = {
        'stops': stops,
        'selected_source': selected_source,
        'selected_dest': selected_dest,
        'results': results,
        'searched': searched,
    }
    return render(request, 'bus_finder/index.html', context)


def api_stops(request):
    """Returns JSON list of all available stops in database."""
    stops = list(Stop.objects.all().order_by('name').values('id', 'name', 'code'))
    return JsonResponse({'status': 'success', 'stops': stops})


def api_search(request):
    """JSON API endpoint for AJAX route search."""
    source_id = request.GET.get('source')
    dest_id = request.GET.get('destination')
    
    if not source_id or not dest_id:
        return JsonResponse({'status': 'error', 'message': 'Source and Destination parameters required.'}, status=400)

    try:
        source_id = int(source_id)
        dest_id = int(dest_id)
    except ValueError:
        return JsonResponse({'status': 'error', 'message': 'Invalid stop IDs provided.'}, status=400)

    results = get_matching_buses(source_id, dest_id)
    
    return JsonResponse({
        'status': 'success',
        'count': len(results),
        'results': results
    })


def get_matching_buses(source_id, dest_id):
    """Core route matching logic."""
    source_stop = Stop.objects.filter(id=source_id).first()
    dest_stop = Stop.objects.filter(id=dest_id).first()

    if not source_stop or not dest_stop or source_stop.id == dest_stop.id:
        return []

    source_bus_stops = BusStop.objects.filter(stop=source_stop, bus__is_active=True)

    results = []
    for s_bs in source_bus_stops:
        bus = s_bs.bus
        d_bs = BusStop.objects.filter(bus=bus, stop=dest_stop, stop_order__gt=s_bs.stop_order).first()
        
        if d_bs:
            all_stops = list(bus.bus_stops.select_related('stop').order_by('stop_order'))
            
            stops_data = []
            for bs in all_stops:
                is_source = (bs.stop_id == source_stop.id)
                is_dest = (bs.stop_id == dest_stop.id)
                is_in_segment = (s_bs.stop_order <= bs.stop_order <= d_bs.stop_order)
                
                stops_data.append({
                    'stop_id': bs.stop.id,
                    'stop_name': bs.stop.name,
                    'stop_order': bs.stop_order,
                    'is_source': is_source,
                    'is_dest': is_dest,
                    'is_in_segment': is_in_segment,
                })

            num_stops_between = d_bs.stop_order - s_bs.stop_order

            results.append({
                'bus_id': bus.id,
                'bus_number': bus.bus_number,
                'route_name': bus.route_name,
                'first_bus_time': bus.first_bus_time.strftime("%I:%M %p") if bus.first_bus_time else "N/A",
                'last_bus_time': bus.last_bus_time.strftime("%I:%M %p") if bus.last_bus_time else "N/A",
                'source_stop': source_stop.name,
                'dest_stop': dest_stop.name,
                'num_stops_between': num_stops_between,
                'stops': stops_data,
                'full_route_str': bus.get_route_display(),
            })

    return results


# ==================== ADMIN AUTHENTICATION VIEWS ==================== #

def admin_login(request):
    """Admin login page view."""
    if request.user.is_authenticated and request.user.is_staff:
        return redirect('bus_finder:admin_dashboard')

    next_url = request.GET.get('next', '')

    if request.method == 'POST':
        username_val = request.POST.get('username', '').strip()
        password_val = request.POST.get('password', '').strip()
        next_url = request.POST.get('next', '')

        user = authenticate(request, username=username_val, password=password_val)
        if user is not None:
            login(request, user)
            messages.success(request, f"Welcome back, {user.username}!")
            if next_url:
                return redirect(next_url)
            return redirect('bus_finder:admin_dashboard')
        else:
            messages.error(request, "Invalid admin username or password. Please try again.")

    return render(request, 'bus_finder/admin_login.html', {'next_url': next_url})


def admin_logout(request):
    """Admin logout view."""
    logout(request)
    messages.success(request, "You have been logged out successfully.")
    return redirect('bus_finder:admin_login')


# ==================== CUSTOM ADMIN PORTAL VIEWS (PROTECTED) ==================== #

@login_required(login_url='bus_finder:admin_login')
def admin_dashboard(request):
    """Custom Admin Portal Dashboard showing all buses, stats, and search."""
    search_query = request.GET.get('q', '').strip()
    
    buses = Bus.objects.all().prefetch_related('bus_stops__stop')
    if search_query:
        buses = buses.filter(
            Q(bus_number__icontains=search_query) | 
            Q(route_name__icontains=search_query) |
            Q(bus_stops__stop__name__icontains=search_query)
        ).distinct()

    total_buses = Bus.objects.count()
    active_buses = Bus.objects.filter(is_active=True).count()
    total_stops = Stop.objects.count()

    context = {
        'buses': buses,
        'search_query': search_query,
        'total_buses': total_buses,
        'active_buses': active_buses,
        'total_stops': total_stops,
    }
    return render(request, 'bus_finder/admin_dashboard.html', context)


@login_required(login_url='bus_finder:admin_login')
def bus_add(request):
    """Custom Admin View to create a new Bus line and define stop route sequence."""
    all_stops = Stop.objects.all().order_by('name')
    
    if request.method == 'POST':
        form = BusForm(request.POST)
        selected_stop_ids = request.POST.getlist('stops[]')
        
        if form.is_valid():
            bus = form.save()
            
            for idx, stop_id in enumerate(selected_stop_ids, start=1):
                if stop_id:
                    stop_obj = Stop.objects.filter(id=stop_id).first()
                    if stop_obj:
                        BusStop.objects.create(bus=bus, stop=stop_obj, stop_order=idx)

            if not bus.route_name:
                bus.route_name = bus.get_route_display()
                bus.save()

            messages.success(request, f"Bus {bus.bus_number} added successfully!")
            return redirect('bus_finder:admin_dashboard')
    else:
        form = BusForm()

    context = {
        'form': form,
        'all_stops': all_stops,
        'page_title': 'Add New Bus Line',
        'is_edit': False,
        'current_stops': [],
    }
    return render(request, 'bus_finder/bus_form.html', context)


@login_required(login_url='bus_finder:admin_login')
def bus_edit(request, bus_id):
    """Custom Admin View to edit an existing Bus and update its stop sequence."""
    bus = get_object_or_404(Bus, id=bus_id)
    all_stops = Stop.objects.all().order_by('name')
    
    if request.method == 'POST':
        form = BusForm(request.POST, instance=bus)
        selected_stop_ids = request.POST.getlist('stops[]')
        
        if form.is_valid():
            bus = form.save()
            
            BusStop.objects.filter(bus=bus).delete()
            for idx, stop_id in enumerate(selected_stop_ids, start=1):
                if stop_id:
                    stop_obj = Stop.objects.filter(id=stop_id).first()
                    if stop_obj:
                        BusStop.objects.create(bus=bus, stop=stop_obj, stop_order=idx)

            messages.success(request, f"Bus {bus.bus_number} updated successfully!")
            return redirect('bus_finder:admin_dashboard')
    else:
        form = BusForm(instance=bus)

    current_stops = list(bus.bus_stops.select_related('stop').order_by('stop_order'))

    context = {
        'form': form,
        'bus': bus,
        'all_stops': all_stops,
        'page_title': f'Edit Bus {bus.bus_number}',
        'is_edit': True,
        'current_stops': current_stops,
    }
    return render(request, 'bus_finder/bus_form.html', context)


@login_required(login_url='bus_finder:admin_login')
def bus_delete(request, bus_id):
    """Custom Admin View to delete a Bus line."""
    bus = get_object_or_404(Bus, id=bus_id)
    bus_number = bus.bus_number
    bus.delete()
    messages.success(request, f"Bus {bus_number} deleted successfully!")
    return redirect('bus_finder:admin_dashboard')


@login_required(login_url='bus_finder:admin_login')
def stop_manage(request):
    """View to list all stops, add new stops, and delete stops."""
    stops = Stop.objects.all().order_by('name')
    
    if request.method == 'POST':
        form = StopForm(request.POST)
        if form.is_valid():
            stop = form.save()
            messages.success(request, f"Stop '{stop.name}' added successfully!")
            return redirect('bus_finder:stop_manage')
    else:
        form = StopForm()

    context = {
        'stops': stops,
        'form': form,
    }
    return render(request, 'bus_finder/stop_manage.html', context)


@login_required(login_url='bus_finder:admin_login')
def stop_delete(request, stop_id):
    """Deletes a bus stop."""
    stop = get_object_or_404(Stop, id=stop_id)
    stop_name = stop.name
    stop.delete()
    messages.success(request, f"Stop '{stop_name}' deleted!")
    return redirect('bus_finder:stop_manage')
