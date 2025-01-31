from .models import Item, ItemType, ItemImage, PartnershipFiles, Partnership, Expenditure, Year
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .forms import ItemForm, ItemTypeForm, ItemImageForm
from reportlab.lib.pagesizes import legal, landscape
from django.views.decorators.csrf import csrf_exempt
from openpyxl.utils import get_column_letter
from django.core.paginator import Paginator
from django.contrib.auth import logout
from decimal import Decimal
from openpyxl.styles import Alignment
from collections import defaultdict
from django.http import HttpResponse, HttpResponseBadRequest
from django.db import IntegrityError
from reportlab.lib.units import inch
from django.contrib import messages
from django.http import HttpResponse
from django.http import FileResponse
from reportlab.lib import colors
from django.conf import settings
from django.urls import reverse
from openpyxl import Workbook
from datetime import datetime
from django.http import JsonResponse
import shutil
import sqlite3
import os


def administrator_dashboard(request):
    return render (request, "administrator/administrator_dashboard.html")

def item_list(request):
    if request.method == 'POST':
        form = ItemForm(request.POST)
        image_form = ItemImageForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                item = form.save()  # Save the item
                # Handle multiple images
                images = request.FILES.getlist('images')
                for image in images:
                    ItemImage.objects.create(item=item, image=image)
                messages.success(request, 'Item added successfully!')
                return redirect('item_list')
            except IntegrityError:  # Catch IntegrityError if it occurs
                messages.error(request, 'An item with this property number already exists.')
        else:
            messages.error(request, 'There was an error adding the item. Please check the form fields.')
    else:
        form = ItemForm()
        image_form = ItemImageForm()

    query = request.GET.get('q', '')
    item_type = request.GET.get('item_type', '')
    items = Item.objects.filter(is_archived=False).order_by("-id")

    if query:
        items = items.filter(property_number__icontains=query)

    if item_type:
        items = items.filter(item_type__id=item_type)

    paginator = Paginator(items, 8)
    page_number = request.GET.get('page')
    page_items = paginator.get_page(page_number)

    item_types = ItemType.objects.all().order_by('name')
    context = {
        'items': page_items,
        'form': form,
        'image_form': image_form,
        'item_types': item_types,
        'query': query,
        'item_type': item_type,
        'export_url': reverse('export_items_to_pdf') + f'?q={query}&item_type={item_type}',
    }
    return render(request, 'administrator/supply_property_inventory.html', context)

def item_type_list(request):
    itemtypes = ItemType.objects.all().order_by('name')  # Fetch all item types

    if request.method == 'POST':
        if 'id' in request.POST:
            # Editing an existing item type
            itemtype = ItemType.objects.get(id=request.POST['id'])
            form = ItemTypeForm(request.POST, request.FILES, instance=itemtype)
            if form.is_valid():
                # Check for duplicate entry
                name = form.cleaned_data.get('name')  # Replace 'name' with your unique field
                if ItemType.objects.filter(name=name).exclude(id=itemtype.id).exists():
                    messages.error(request, 'An item type with this name already exists.')
                else:
                    form.save()
                    messages.success(request, 'Item type updated successfully!')
                    return redirect('item_type_list')  # Redirect after successful update
            else:
                messages.error(request, 'Failed to update item type. Please try again.')
        else:
            # Adding a new item type
            form = ItemTypeForm(request.POST, request.FILES)
            if form.is_valid():
                # Check for duplicate entry
                name = form.cleaned_data.get('name')  # Replace 'name' with your unique field
                if ItemType.objects.filter(name=name).exists():
                    messages.error(request, 'An item type with this name already exists.')
                else:
                    form.save()
                    messages.success(request, 'Item type added successfully!')
                    return redirect('item_type_list')  # Redirect after adding
            else:
                messages.error(request, 'Failed to add item type. Please try again.')

    else:
        form = ItemTypeForm()  # Create an empty form for the modal

    return render(request, 'administrator/item_type_list.html', {
        'itemtypes': itemtypes,
        'form': form,
    })


def edit_item_type(request, pk):
    item_type = get_object_or_404(ItemType, pk=pk)

    if request.method == "POST":
        form = ItemTypeForm(request.POST, request.FILES, instance=item_type)
        if form.is_valid():
            form.save()  # Save the updated item type (name and image)
            messages.success(request, f"Item type '{item_type.name}' updated successfully.")
        else:
            messages.error(request, "Failed to update item type. Please try again.")
        return redirect('item_type_list')  # Redirect to the list view after editing

    form = ItemTypeForm(instance=item_type)  # If GET, populate the form with existing item type details
    return render(request, 'administrator/item_type_list.html', {'form': form, 'item_type': item_type})

def delete_item_type(request, pk):
    item_type = get_object_or_404(ItemType, pk=pk)
    try:
        if request.method == "POST":
            item_type.delete()
            messages.success(request, f"Item type '{item_type.name}' has been deleted successfully.")
            return redirect('item_type_list')  # Replace with the name of your list view's URL
    except IntegrityError:
        messages.error(request, f"Cannot delete '{item_type.name}' because there are related records.")
        return redirect('item_type_list')  # Return to the list if there's an error
    return redirect('item_type_list')  # Ensure redirection if the method is not POST

def item_detail(request, id):
    item = get_object_or_404(Item, id=id)
    item_types = ItemType.objects.all()  # Fetch all item types
    return render(request, 'administrator/item_detail.html', {'item': item, 'item_types': item_types})
def item_edit(request, id):
    item = get_object_or_404(Item, id=id)

    if request.method == "POST":
        try:
            item.sector_office_division_college = request.POST['sector_office_division_college']
            item.operating_unit_project = request.POST['operating_unit_project']
            item.property_number = request.POST['property_number']
            item.responsible_person = request.POST['responsible_person']
            item.quantity = request.POST['quantity']
            item.unit = request.POST['unit']

            # Fetch the ItemType instance before assigning it
            item_type_id = request.POST['item_type']
            item.item_type = get_object_or_404(ItemType, id=item_type_id)

            item.description = request.POST['description']
            item.date_acquired = request.POST['date_acquired']
            item.fund = request.POST['fund']
            item.ppe_class = request.POST['ppe_class']
            item.estimated_useful_life = request.POST['estimated_useful_life']
            item.unit_price = request.POST['unit_price']
            item.total_amount = request.POST['total_amount']
            item.remarks = request.POST['remarks']  # Add remarks field
            item.is_archived = 'is_archived' in request.POST
            
            item.save()

            # Save uploaded images
            if request.FILES.getlist('images'):
                for image in request.FILES.getlist('images'):
                    ItemImage.objects.create(item=item, image=image)

            messages.success(request, "Item successfully updated.")
            return redirect('item_detail_admin', id=item.id)
        except Exception as e:
            messages.error(request, f"Error updating item: {str(e)}")

    item_types = ItemType.objects.all()
    return render(request, 'administrator/item_detail.html', {'item': item, 'item_types': item_types})

def add_item_image(request, id):
    item = get_object_or_404(Item, id=id)
    
    if request.method == "POST":
        try:
            if request.FILES.getlist('images'):
                for image in request.FILES.getlist('images'):
                    ItemImage.objects.create(item=item, image=image)
            messages.success(request, "Image(s) added successfully.")
        except Exception as e:
            messages.error(request, f"Error adding image(s): {str(e)}")
    
    return redirect('item_edit', id=item.id)


def edit_item_image(request, id):
    item = get_object_or_404(Item, id=id)

    if request.method == "POST":
        image_id = request.POST.get('image_id')
        new_image = request.FILES.get('new_image')
        
        try:
            image_instance = get_object_or_404(ItemImage, id=image_id, item=item)
            if new_image:
                image_instance.image = new_image
                image_instance.save()
                messages.success(request, "Image updated successfully.")
            else:
                messages.error(request, "Please select a new image.")
        except Exception as e:
            messages.error(request, f"Error updating image: {str(e)}")
    
    return redirect('item_detail_admin', id=item.id)

def delete_item_image(request, id):
    item = get_object_or_404(Item, id=id)

    if request.method == "POST":
        image_id = request.POST.get('image_id')
        
        try:
            image_instance = get_object_or_404(ItemImage, id=image_id, item=item)
            image_instance.delete()  # Delete the image instance
            messages.success(request, "Image deleted successfully.")
        except Exception as e:
            messages.error(request, f"Error deleting image: {str(e)}")

    return redirect('item_detail_admin', id=item.id)

def export_items_to_excel(request):
    # Create a new workbook and active sheet
    workbook = Workbook()
    sheet = workbook.active
    sheet.title = 'Items'

    # Define headers for the sheet
    headers = [
        "Sector/Office/Division/College", "Operating Unit/Project", "Property Number", 
        "Responsible Person", "Quantity", "Unit", "Type", "Item Description", 
        "Date Acquired", "Fund", "PPE Class", "Estimated Useful Life", 
        "Unit Price (₱)", "Total Amount (₱)"
    ]
    sheet.append(headers)

    # Filters from the GET request
    query = request.GET.get('q', '')
    item_type_id = request.GET.get('item_type', '')

    items = Item.objects.all().order_by("-date_acquired")

    # Apply search filter
    if query:
        items = items.filter(property_number__icontains=query)

    # Apply item type filter and get item type name for filename
    item_type_name = "Items"
    if item_type_id:
        item_type = ItemType.objects.filter(id=item_type_id).first()
        if item_type:
            item_type_name = item_type.name
            items = items.filter(item_type=item_type)

    # Write data to the sheet
    for item in items:
        unit_price = f"₱{item.unit_price:,.2f}" if item.unit_price else ''
        total_amount = f"₱{item.total_amount:,.2f}" if item.total_amount else ''
        
        sheet.append([
            item.sector_office_division_college,
            item.operating_unit_project,
            item.property_number,
            item.responsible_person,
            item.quantity,
            item.unit,
            item.item_type.name if item.item_type else '',
            item.description,
            item.date_acquired.strftime("%B %d, %Y") if item.date_acquired else '',
            item.fund,
            item.ppe_class,
            f"{item.estimated_useful_life} years" if item.estimated_useful_life else '',
            unit_price,
            total_amount
        ])

    # Auto-adjust column widths and wrap text for description
    for col_num, column_cells in enumerate(sheet.columns, 1):
        max_length = 0
        col_letter = get_column_letter(col_num)
        for cell in column_cells:
            try:
                if cell.value:
                    max_length = max(max_length, len(str(cell.value)))
                    if col_letter == get_column_letter(8):  # Wrap text for 'Item Description'
                        cell.alignment = Alignment(wrap_text=True)
            except Exception as e:
                print(e)
        sheet.column_dimensions[col_letter].width = max_length + 2

    # Set the response to send an Excel file with a dynamic filename
    filename = f"{item_type_name.replace(' ', '_')}.xlsx"
    response = HttpResponse(
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    )
    response['Content-Disposition'] = f'attachment; filename={filename}'
    workbook.save(response)
    return response

def archive_item(request, item_id):
    item = get_object_or_404(Item, id=item_id)

  
    item.is_archived = True
    item.save()


    messages.success(request, f"The item '{item.property_number}' has been archived successfully.")


    return redirect('item_list')  


# Function to wrap text inside a Paragraph for better visibility
def wrap_text(text, font_name='Helvetica'):
    """Wrap text inside a Paragraph to avoid truncating."""
    style = ParagraphStyle(name='Normal', fontSize=7, wordWrap='LTR', fontName=font_name)
    return Paragraph(text, style)

def export_items_to_pdf(request):
    # Get search filters from GET request
    query = request.GET.get('q', '')
    item_type = request.GET.get('item_type', '')

    # Create HttpResponse object with PDF headers
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="items_report.pdf"'
    
    # Create a PDF document with reduced margins and landscape legal size
    doc = SimpleDocTemplate(response, pagesize=landscape(legal),
                            leftMargin=0.5 * inch, rightMargin=0.5 * inch, 
                            topMargin=0.5 * inch, bottomMargin=0.3 * inch)
    
    elements = []
    
    # Define styles
    styles = getSampleStyleSheet()
    header_style = styles['BodyText']
    header_style.fontSize = 7
    header_style.leading = 9
    header_style.fontName = 'Helvetica-Bold'  # Use Helvetica-Bold for header
    header_style.textColor = colors.whitesmoke  # Set text color to white

    # Shortened headers with wrapping
    def header_text(text):
        return Paragraph(text, header_style)
    
    # Prepare the header data
    data = [
        [
            header_text("Sector/<br/>Office/Division"),
            header_text("Operating <br/>Unit/Project"),
            "Prop. No.",
            "Resp. Person",
            "Qty", "Unit", "Type", 
            header_text("Item Description"),
            "Date Acquired", "Fund", "PPE Class", 
            "Useful Life", "Unit Price", "Total"
        ]
    ]
    
    # Fetch items and apply search filters
    items = Item.objects.all()

    # Apply search filter
    if query:
        items = items.filter(property_number__icontains=query)

    # Apply item type filter
    if item_type:
        items = items.filter(item_type__id=item_type)

    # Wrap each field for each item
    for item in items:
        data.append([ 
            wrap_text(item.sector_office_division_college),
            wrap_text(item.operating_unit_project),
            wrap_text(item.property_number),
            wrap_text(item.responsible_person),
            item.quantity, item.unit,
            wrap_text(item.item_type.name),
            wrap_text(item.description),
            item.date_acquired.strftime('%B %d, %Y'),
            wrap_text(item.fund),
            wrap_text(item.ppe_class),
            f"{item.estimated_useful_life} yrs",
            wrap_text(f"P{item.unit_price:,.2f}"),  # Removed custom font for unit price
            wrap_text(f"P{item.total_amount:,.2f}")  # Removed custom font for total
        ])
    
    # Adjust column widths
    col_widths = [
        0.9 * inch, 0.9 * inch, 1.2 * inch,
        1.2 * inch, 0.4 * inch, 0.5 * inch, 
        0.9 * inch, 1.8 * inch, 1.0 * inch,
        0.9 * inch, 0.9 * inch, 0.7 * inch,
        0.8 * inch, 0.8 * inch
    ]
    
    # Create and style the table
    table = Table(data, colWidths=col_widths)
    table.setStyle(TableStyle([ 
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),  # Keep using Helvetica-Bold
        ('FONTSIZE', (0, 0), (-1, -1), 7),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 5),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
        ('VALIGN', (0, 1), (-1, -1), 'TOP'),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
    ]))
    
    elements.append(table)
    doc.build(elements)
    
    return response


def archived_items_view(request):
    # Filter archived items
    archived_items = Item.objects.filter(is_archived=True)

    # Paginate the results
    from django.core.paginator import Paginator
    paginator = Paginator(archived_items, 10)  # Show 10 items per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Pass the items to the template
    return render(request, 'administrator/archived_items.html', {'items': page_obj})

def unarchive_item(request, item_id):
    # Ensure that the user has the proper permissions
    item = get_object_or_404(Item, id=item_id)
    
    # Check if the item is archived before allowing unarchiving
    if not item.is_archived:
        # Item is not archived, show an error message
        messages.error(request, "This item is not archived and cannot be restored.")
        return redirect('item_list')  # Change to the appropriate view if needed
    
    # Unarchive the item
    item.is_archived = False
    item.save()

    # Show a success message
    messages.success(request, f"The item '{item.property_number}' has been successfully restored.")

    # Redirect back to the item list or relevant page
    return redirect('item_list')  # Change 'item_list' to your relevant view


@login_required    
def download_db_backup(request):
    db_path = os.path.join(settings.BASE_DIR, 'db.sqlite3')
    if os.path.exists(db_path):
        # Format the date in 'YYYY-MM-DD' format
        date_str = datetime.now().strftime("%B %d, %Y")
        filename = f"db_backup_{date_str}.sqlite3"
        
        response = FileResponse(open(db_path, 'rb'), content_type='application/x-sqlite3')
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        return response
    else:
        return HttpResponse("Database file not found.", status=404)

def restore_database(request):
    if request.method == 'POST' and request.FILES.get('db_file'):
        db_file = request.FILES['db_file']
        
        # Confirm file type is correct
        if not db_file.name.endswith('.sqlite3'):
            messages.error(request, "Please upload a valid SQLite3 database file (.sqlite3).")
            return redirect('restore_database')

        # Paths for backup and current database
        backup_path = os.path.join(settings.BASE_DIR, 'db_backup.sqlite3')
        current_db_path = os.path.join(settings.BASE_DIR, 'db.sqlite3')
        temp_db_path = os.path.join(settings.BASE_DIR, 'temp_uploaded_db.sqlite3')

        try:
            # Save uploaded file temporarily
            with open(temp_db_path, 'wb+') as temp_db:
                for chunk in db_file.chunks():
                    temp_db.write(chunk)
            
            # Check table structure in current and uploaded databases
            def get_table_names(db_path):
                conn = sqlite3.connect(db_path)
                cursor = conn.cursor()
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
                tables = {table[0] for table in cursor.fetchall()}
                conn.close()
                return tables

            current_tables = get_table_names(current_db_path)
            uploaded_tables = get_table_names(temp_db_path)
            
            # Verify table structure
            if current_tables != uploaded_tables:
                messages.error(request, "The uploaded database does not have the same structure as the current database.")
                os.remove(temp_db_path)  # Remove temporary uploaded database file
                return redirect('restore_database')

            # Backup current database
            if os.path.exists(current_db_path):
                shutil.copy(current_db_path, backup_path)
            
            # Replace current database with uploaded file
            shutil.move(temp_db_path, current_db_path)
            messages.success(request, "Database restored successfully!")

        except Exception as e:
            # Restore from backup if something goes wrong
            if os.path.exists(backup_path):
                shutil.copy(backup_path, current_db_path)

            messages.error(request, f"An error occurred while restoring: {str(e)}")
            return redirect('restore_database')

        return redirect('restore_database')

    return render(request, 'administrator/restore_database.html')

def logout_view(request):
    logout(request)
    messages.success(request, "You have been Logged-Out Successfully!")
    return redirect('login_url')


def partnership_list(request):
    if request.method == 'POST':
        try:
            # Get the data from the POST request
            partner = request.POST.get('partner')
            country = request.POST.get('country')
            continent = request.POST.get('continent')
            type_of_organization = request.POST.get('type_of_organization')
            description = request.POST.get('description')
            status = request.POST.get('status')
            logo = request.FILES.get('logo')  # Handle the logo file upload
            university_files = request.FILES.getlist('university_files')  # Handle multiple files

            # Create the partnership object
            partnership = Partnership.objects.create(
                partner=partner,
                country=country,
                continent=continent,
                type_of_organization=type_of_organization,
                description=description,
                status=status,
                logo=logo
            )

            # Save each file as a PartnershipFiles object
            for file in university_files:
                PartnershipFiles.objects.create(
                    partnership=partnership,
                    file=file
                )

            messages.success(request, 'Partnership added successfully!')
        except Exception as e:
            messages.error(request, f'Failed to add partnership: {str(e)}')

        return redirect('partnership_list')

    # Handling GET request (displaying the partnership list)
    query = request.GET.get('q', '')
    continent_filter = request.GET.get('continent', '')
    status_filter = request.GET.get('status', '')  # Get the status filter from the request

    partnerships = Partnership.objects.all().order_by("partner").filter(is_removed_from_list=False)

    # Apply search filter
    if query:
        partnerships = partnerships.filter(
            partner__icontains=query
        ) | partnerships.filter(
            country__icontains=query
        ) | partnerships.filter(
            type_of_organization__icontains=query
        )

    # Apply continent filter
    if continent_filter:
        partnerships = partnerships.filter(continent=continent_filter)

    # Apply status filter
    if status_filter:
        partnerships = partnerships.filter(status=status_filter)

    # Apply pagination
    paginator = Paginator(partnerships, 10)  # Show 10 partnerships per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'partnerships': page_obj,
        'query': query,
        'continent_filter': continent_filter,
        'status_filter': status_filter,  # Pass the status filter to the template
        'CONTINENT_CHOICES': Partnership.CONTINENT_CHOICES,
        'STATUS_CHOICES': Partnership.STATUS_CHOICES,  # Pass status choices to the template
    }

    return render(request, 'administrator/partnership_list.html', context)

def partnership_detail(request, partnership_id):
    partnership = get_object_or_404(Partnership, id=partnership_id)
    partnership_files = partnership.files.all()  # Get the files related to this partnership

    # Pass choices for continent and status to the template
    continent_choices = Partnership.CONTINENT_CHOICES
    status_choices = Partnership.STATUS_CHOICES

    if request.method == 'POST':
        partnership.partner = request.POST.get('partner')
        partnership.country = request.POST.get('country')
        partnership.continent = request.POST.get('continent')
        partnership.type_of_organization = request.POST.get('type_of_organization')
        partnership.description = request.POST.get('description')
        partnership.status = request.POST.get('status')
        
        if request.FILES.get('logo'):
            partnership.logo = request.FILES['logo']
        
        partnership.save()
        messages.success(request, 'Partnership updated successfully!')
        return redirect('partnership_detail', partnership_id=partnership.id)

    context = {
        'partnership': partnership,
        'partnership_files': partnership_files,
        'continent_choices': continent_choices,
        'status_choices': status_choices,
    }
    return render(request, 'administrator/partnership_detail.html', context)


def upload_file_to_partnership(request, partnership_id):
    if request.method == 'POST':
        partnership = get_object_or_404(Partnership, id=partnership_id)
        file = request.FILES.get('file')
        description = request.POST.get('description')

        if file:
            PartnershipFiles.objects.create(
                partnership=partnership,
                file=file,
                description=description
            )
            messages.success(request, "File uploaded successfully!")
        else:
            messages.error(request, "File is required.")

    return redirect('partnership_detail', partnership_id=partnership_id)


@csrf_exempt
def delete_partnership_file(request):
    if request.method == 'POST':
        file_id = request.POST.get('file_id')
        if not file_id:
            return JsonResponse({'success': False, 'error': 'Missing file_id'})
        
        try:
            file = PartnershipFiles.objects.get(id=file_id)
            file.delete()  # Delete the file from the database and storage

          
            # Send a success response back to the client
            return JsonResponse({'success': True})
        
        except PartnershipFiles.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'File not found'})
    
    return JsonResponse({'success': False, 'error': 'Invalid request method'})

def expenditure_list(request):
    # Group expenditures by classification
    expenditures = Expenditure.objects.all().order_by("classification", "expenditure_type", "item_number")
    grouped_expenditures = {}
    
    for expenditure in expenditures:
        classification = expenditure.classification
        if classification not in grouped_expenditures:
            grouped_expenditures[classification] = {}
        
        expenditure_type = expenditure.expenditure_type
        if expenditure_type not in grouped_expenditures[classification]:
            grouped_expenditures[classification][expenditure_type] = []

        grouped_expenditures[classification][expenditure_type].append(expenditure)

    # Pass the grouped expenditures and classification choices to the template
    context = {
        "grouped_expenditures": grouped_expenditures,
        "classification_choices": Expenditure.CLASSIFICATION_CHOICES,  # Add classification choices
    }
    return render(request, "administrator/expenditure_details.html", context)


def add_expenditure(request, year_id):
    year = get_object_or_404(Year, id=year_id)  # Get the selected year

    if request.method == 'POST':
        # Extract data from the form
        classification = request.POST.get('classification')
        expenditure_type = request.POST.get('expenditure_type')
        description = request.POST.get('description')
        mode_of_procurement = request.POST.get('mode_of_procurement')
        quarter1 = int(request.POST.get('quarter1', 0))
        quarter2 = int(request.POST.get('quarter2', 0))
        quarter3 = int(request.POST.get('quarter3', 0))
        quarter4 = int(request.POST.get('quarter4', 0))
        unit_of_measure = request.POST.get('unit_of_measure')
        unit_price = float(request.POST.get('unit_price'))
        remarks = request.POST.get('remarks', '')

        # Create and save the new expenditure
        try:
            expenditure = Expenditure(
                year=year,  # Associate the expenditure with the selected year
                classification=classification,
                expenditure_type=expenditure_type,
                description=description,
                mode_of_procurement=mode_of_procurement,
                quarter1=quarter1,
                quarter2=quarter2,
                quarter3=quarter3,
                quarter4=quarter4,
                unit_of_measure=unit_of_measure,
                unit_price=unit_price,
                remarks=remarks
            )
            expenditure.save()
            messages.success(request, 'Expenditure added successfully!')
        except Exception as e:
            messages.error(request, f'Error adding expenditure: {str(e)}')

        return redirect('year_detail', year_id=year_id)  # Redirect back to the year detail page

    return redirect('year_detail', year_id=year_id)  # Redirect if not a POST request

def year_list(request):
    # Fetch all Year instances from the database
    years = Year.objects.all()
    
    # Pass the years to the template
    context = {
        'years': years,
    }
    
    return render(request, 'administrator/year_list.html', context)


def year_detail(request, year_id):
    year = get_object_or_404(Year, id=year_id)
    expenditures = Expenditure.objects.filter(year=year).order_by("classification", "expenditure_type", "item_number")

    grouped_expenditures = {}
    subtotals = defaultdict(lambda: defaultdict(lambda: Decimal(0)))
    totals_per_classification = defaultdict(Decimal)
    grand_total = Decimal(0)

    for expenditure in expenditures:
        classification = expenditure.classification
        expenditure_type = expenditure.expenditure_type

        if classification not in grouped_expenditures:
            grouped_expenditures[classification] = {}

        if expenditure_type not in grouped_expenditures[classification]:
            grouped_expenditures[classification][expenditure_type] = []

        grouped_expenditures[classification][expenditure_type].append(expenditure)

        # Compute subtotal for expenditure type
        subtotals[classification][expenditure_type] += Decimal(expenditure.total_amount)

        # Compute total per classification
        totals_per_classification[classification] += Decimal(expenditure.total_amount)

        # Compute grand total
        grand_total += Decimal(expenditure.total_amount)

    context = {
    "grouped_expenditures": grouped_expenditures,
    "subtotals": {k: dict(v) for k, v in subtotals.items()},  # Convert nested defaultdict to dict
    "totals_per_classification": dict(totals_per_classification),  # Convert defaultdict to dict
    "grand_total": grand_total,
    "classification_choices": Expenditure.CLASSIFICATION_CHOICES,
    "selected_year": year,
    }

    return render(request, "administrator/year_detail.html", context)