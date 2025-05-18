import io
from django.shortcuts import render, redirect, get_object_or_404
from google.cloud import vision
from django.core.files.uploadedfile import InMemoryUploadedFile
from .forms import RoomForm, ContainerForm, ItemContainerForm
from .models import Room, Container, Item
import base64
from PIL import Image
import os
from django.http import HttpResponse


def resize_image(image_file, max_size=(1920, 1080)):
    """Resize image while maintaining aspect ratio"""
    # Open image using Pillow
    img = Image.open(image_file)
    
    # Convert to RGB if necessary (for PNG with transparency)
    if img.mode in ('RGBA', 'LA'):
        background = Image.new('RGB', img.size, (255, 255, 255))
        background.paste(img, mask=img.split()[-1])
        img = background
    
    # Calculate new size maintaining aspect ratio
    ratio = min(max_size[0]/img.size[0], max_size[1]/img.size[1])
    new_size = tuple([int(x*ratio) for x in img.size])
    
    # Resize image
    img = img.resize(new_size, Image.Resampling.LANCZOS)
    
    # Save to bytes
    output = io.BytesIO()
    img.save(output, format='JPEG', quality=85, optimize=True)
    output.seek(0)
    
    return output

def upload_image(request):
    result = None
    containers = Container.objects.all().select_related('location')
    
    if request.method == "POST":
        image_data = request.POST.get('image')
        container_id = request.POST.get('container')
        if image_data:
            try:
                # Handle base64 image data
                if image_data.startswith('data:image'):
                    # Remove the data URL prefix
                    image_data = image_data.split(',')[1]
                    # Convert base64 to bytes
                    image_bytes = base64.b64decode(image_data)
                    # Create a file-like object
                    image_file = io.BytesIO(image_bytes)
                    
                    # Resize image before processing
                    resized_image = resize_image(image_file)
                    
                    # Create an InMemoryUploadedFile for storage
                    resized_image.seek(0)
                    image = InMemoryUploadedFile(
                        resized_image,
                        field_name='image',
                        name='camera_image.jpg',
                        content_type='image/jpeg',
                        size=len(resized_image.getvalue()),
                        charset=None
                    )
                else:
                    # Handle regular file upload
                    image = request.FILES.get('image')
                    if image:
                        # Resize image before processing
                        resized_image = resize_image(image)
                        resized_image.seek(0)
                        image = InMemoryUploadedFile(
                            resized_image,
                            field_name='image',
                            name=image.name,
                            content_type=image.content_type,
                            size=len(resized_image.getvalue()),
                            charset=None
                        )
                
                if image:
                    if int(os.getenv("USE_GOOGLE_VISION")) != 0:
                        client = vision.ImageAnnotatorClient()
                        
                        # Read image content
                        content = image.read()
                        image_vision = vision.Image(content=content)
                        features = []

                        # Wykrywanie tekstu
                        text_response = client.text_detection(image=image_vision)
                        text_annotations = text_response.text_annotations
                        text = text_annotations[0].description if text_annotations else "Brak wykrytego tekstu"
                        features.append({"type": "text", "content": text})

                        # Wykrywanie obiektów
                        label_response = client.label_detection(image=image_vision)
                        labels = [label.description for label in label_response.label_annotations]
                        features.append({"type": "labels", "content": labels})

                        # Reset file pointer for storage
                        image.seek(0)
                    else:
                        features = []
                        labels = []
                        text = ""
                    
                    # Get container if selected
                    container = None
                    if container_id:
                        container = Container.objects.get(id=container_id)
                    
                    # Create name from text or first two labels
                    if text and text != "Brak wykrytego tekstu":
                        name = text[:50] + "..." if len(text) > 50 else text
                    else:
                        # Use first two labels as name
                        name = " - ".join(labels[:2]) if len(labels) >= 2 else labels[0] if labels else "Unnamed Item"
                    
                    item = Item.objects.create(
                        name=name,
                        features=features,
                        image=image,
                        container=container
                    )
                    
                    # Redirect to item detail page
                    return redirect('item_detail', item_id=item.id)
            except Exception as e:
                print(f"Error processing image: {str(e)}")
                return HttpResponse(str(e))
                # You might want to add error handling here

    return render(request, "box_scanner/upload.html", {
        "result": result,
        "containers": containers
    })

def add_room(request):
    if request.method == "POST":
        name = request.POST["name"]
        color = request.POST["color"]
        Room.objects.create(name=name, color=color)
        return redirect("add_room")
    
    return render(request, "box_scanner/add_room.html")


def add_container(request):
    rooms = Room.objects.all()
    if request.method == "POST":
        name = request.POST["name"]
        room_id = request.POST["room"]
        room = Room.objects.get(id=room_id)
        Container.objects.create(name=name, location=room)
        return redirect("add_container")
    
    return render(request, "box_scanner/add_container.html", {"rooms": rooms})

def container_browser(request):
    search_query = request.GET.get('search', '')
    room_id = request.GET.get('room')
    containers = Container.objects.all().select_related('location')
    rooms = Room.objects.all()
    
    # Filter containers by room if room_id is provided
    if room_id:
        containers = containers.filter(location_id=room_id)
        current_room = Room.objects.get(id=room_id)
    else:
        current_room = None
    
    if request.method == 'POST':
        name = request.POST.get('name')
        room_id = request.POST.get('room')
        if name and room_id:
            room = Room.objects.get(id=room_id)
            Container.objects.create(name=name, location=room)
            return redirect('container_browser')
    
    if search_query:
        containers = containers.filter(name__icontains=search_query)
    
    return render(request, "box_scanner/container_browser.html", {
        "containers": containers,
        "search_query": search_query,
        "rooms": rooms,
        "current_room": current_room
    })

def item_list(request):
    container_id = request.GET.get('container')
    search_query = request.GET.get('search', '')
    items = Item.objects.all().select_related('container', 'container__location')
    
    if container_id:
        items = items.filter(container_id=container_id)
        container = Container.objects.get(id=container_id)
    else:
        container = None
    
    if search_query:
        # Search in name
        name_matches = items.filter(name__icontains=search_query)
        
        # Search in features
        # Convert features to string and search in the string representation
        feature_matches = items.filter(features__icontains=search_query)
        
        # Combine matches
        items = (name_matches | feature_matches).distinct()
    
    return render(request, "box_scanner/item_list.html", {
        "items": items,
        "container": container,
        "search_query": search_query
    })

def item_detail(request, item_id):
    item = get_object_or_404(Item, id=item_id)
    containers = Container.objects.all().select_related('location')
    
    if request.method == "POST" and 'update_details' in request.POST:
        # Update name
        new_name = request.POST.get('name')
        if new_name:
            item.name = new_name
        
        # Update features
        features = []
        
        # Update text feature
        text_content = request.POST.get('text_content')
        if text_content is not None:
            features.append({"type": "text", "content": text_content})
        
        # Update labels
        labels = []
        # Get existing labels from checkboxes
        for key, value in request.POST.items():
            if key.startswith('label_') and value == 'on':
                labels.append(key.replace('label_', ''))
        
        # Add new label if provided
        new_label = request.POST.get('new_label')
        if new_label and new_label.strip():
            labels.append(new_label.strip())
        
        if labels:
            features.append({"type": "labels", "content": labels})
        
        if features:
            item.features = features
        
        # Update container
        container_id = request.POST.get('container')
        if container_id:
            container = get_object_or_404(Container, id=container_id)
            item.container = container
        else:
            item.container = None
        
        item.save()
        return redirect('item_detail', item_id=item.id)
    
    # Get current labels for template
    current_labels = []
    for feature in item.features:
        if feature['type'] == 'labels':
            current_labels = feature['content']
            break
    
    return render(request, "box_scanner/item_detail.html", {
        "item": item,
        "containers": containers,
        "current_labels": current_labels
    })

def room_browser(request):
    rooms = Room.objects.all()
    
    if request.method == 'POST':
        name = request.POST.get('name')
        if name:
            Room.objects.create(name=name)
            return redirect('room_browser')
    
    return render(request, "box_scanner/room_browser.html", {
        "rooms": rooms
    })


