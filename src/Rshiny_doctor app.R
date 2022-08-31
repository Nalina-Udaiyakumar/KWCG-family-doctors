# This is a Shiny application
# This app creates a dashboard similar to the Python dash version.

library(shinythemes)
library(shinyWidgets)
library(shiny)
library(DT)
library(geosphere)

setwd("--Your directory path---")
getwd()

distanceTable <- read.csv("UniqueKWCGcodes.csv",header=TRUE)
dim(distanceTable)

KWCGpostalcodes <- read.csv("KWCGpostcodes_Latlong.csv",header=TRUE)
dim(KWCGpostalcodes)

KWCGdoctors <- read.csv("Results_family doctors KWCG.csv",header=TRUE)
dim(KWCGdoctors)

# filter only the rquired columns in KWCGdoctors
KWCGdoctors <- KWCGdoctors[,c('Name','CPSOID','Location','Phone','City','Postal.Code','Additional.Locations')]

#set global options for page length and filter action of DT
options(DT.options = list(pageLength = 5, language = list(search = 'Filter:')))

# Define UI elements
ui <- fluidPage(
  # theme = bs_theme(version = 4, bootswatch = "minty"),

    # Application title
    titlePanel("KW region family doctor search", "color:#3474A7"),

    # Sidebar with a slider input for filtering the search
    sidebarLayout(
        sidebarPanel(
          radioButtons(
            "modeRadio",
            "Search doctors by:",
            choices = c('Location','Distance'),
            selected = c('Location'),
            inline=TRUE),
          
          selectInput(
            "locationDropdown",
            "Select city/cities to filter:",
            KWCGdoctors$City,
            selected = NULL,
            multiple = TRUE),
          
          textInput(
            "postalCode", 
            "Enter postal code: (Ex: N2M 0A1)", 
            value = "",
            placeholder = "N2M 0A1"),
          
          sliderInput("distance",
                      "Select radius of search:",
                      min = 5,
                      max = 50,
                      value = 10,
                      step=5),
            
        ),

        # Data table with doctors and their relevant information
        mainPanel(
          DTOutput("doctorTable")
        )
    )
)

# Define server logic 
server <- function(input, output) 
  {
  
  
  output$doctorTable <- renderDT({
    filteredDoctors <- KWCGdoctors
    
    ## Location search
    if(input$modeRadio == 'Location')
    {
      if(!is.null(input$locationDropdown))
      {
        filteredDoctors <- KWCGdoctors[KWCGdoctors$City %in% input$locationDropdown,]
      }
    }
    
    ## Distance search
    else
    {
      filteredDoctors <- KWCGdoctors[,c('Name','CPSOID','Location','Phone','City','Postal.Code','Additional.Locations')]
      if(!is.null(input$postalCode))
        pcode <- input$postalCode
        
      else if(is.null(input$postalCode))
        pcode <- "N2M 0A1"
        
      
      latgiven <- KWCGpostalcodes[KWCGpostalcodes$Postalcode==pcode,'Latitude']
      longgiven <- KWCGpostalcodes[KWCGpostalcodes$Postalcode==pcode,'Longitude']
      
      filteredDoctors <- filteredDoctors[filteredDoctors$Postal.Code != "",]
      filteredDoctors <- merge(x=filteredDoctors,y=KWCGpostalcodes, 
                               by.x='Postal.Code',by.y='Postalcode',
                               all.x=T)
      # renaming City.x column to City in filteredDoctors after join
      names(filteredDoctors)[names(filteredDoctors) == 'City.x'] <- 'City'
      
      filteredDoctors$latgiven <- latgiven
      filteredDoctors$longgiven <- longgiven
      
      # Calculating distance between doctor's offices and the given postal code
      filteredDoctors$distance <- distHaversine(filteredDoctors[,c('Latitude','Longitude')], 
                                                filteredDoctors[,c('latgiven','longgiven')])
      filteredDoctors$distance <- filteredDoctors$distance/1000
      
      filteredDoctors <- filteredDoctors[!is.na(filteredDoctors$distance),]
      
      filteredDoctors <- filteredDoctors[order(filteredDoctors$distance,decreasing = F),]
      filteredDoctors <- filteredDoctors[filteredDoctors$distance <= input$distance,
                                         c('Name','CPSOID','Location','Phone','City','Postal.Code','Additional.Locations')]
        
    }
    filteredDoctors
    
    })
    
  }  



# Run the application 
shinyApp(ui = ui, server = server)
