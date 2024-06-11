library(shiny)

df <- read.csv('Batting_Data.csv')[,1:7]
launch_angles <- seq(-60, 90, 2)
la0 <- which(launch_angles == 0)

get_batter_data <- function(batter_df) {
  nobs <- nrow(batter_df)
  vals <- t(vapply(launch_angles, function(la) {
    filtered_events <- batter_df[batter_df[,'launch_angle'] >= la - 10 & batter_df[,'launch_angle'] <= la + 10,]
    total <- nrow(filtered_events)
    squared_up_rate <- mean(filtered_events[,'squared_up'])
    obs_percentage <- total / nobs * 100
    c(la, squared_up_rate, total, obs_percentage)
  }, numeric(4)))
  ix <- vals[,3] <= 20
  if(all(ix)) return(NULL)
  vals[ix,2] <- NA
  colnames(vals) <- c('launch_angle', 'squared_up_rate', 'total_events', 'obs_percentage')
  data.frame(batter = batter_df[1,'Name'], vals)
}
ldat <- split(df, df[,'Name'])
alldat <- lapply(ldat, get_batter_data)
# remove empty data (like Aaron Hicks)
alldat <- alldat[lengths(alldat) > 0]

get_plot <- function(...) {
  bens_colors <- c('#50ae26', '#74b4fa', '#ce2431')
  args <- list(...)
  args <- intersect(names(alldat), unlist(args))
  if(length(args) == 0) return(NULL)
  pnames <- args[1]
  d1 <- alldat[[args[1]]]
  r1 <- range(which(!is.na(d1$squared_up_rate)))
  r1[is.infinite(r1)] <- la0
  r2 <- rep(la0, 2)
  if(length(args) > 1) {
    pnames <- c(pnames, args[2])
    d2 <- alldat[[args[2]]]
    r2 <- range(which(!is.na(d2$squared_up_rate)))
    r2[is.infinite(r2)] <- la0
  }
  rng <- launch_angles[range(c(r1, r2))]
  if(length(rng) == 1) rng <- rep(rng, 2)
  xlim <- c(floor(rng[1] / 10) * 10, ceiling(rng[2] / 10) * 10)

  main_title <- sprintf('Squared-Up Rate vs. Launch Angle for Batters:\n%s', paste(pnames, collapse = ', '))
  plot(d1$launch_angle, d1$squared_up_rate * 100, xlim = xlim, ylim = c(0, 100),
       main = main_title,
       xlab = 'Launch Angle (degrees)',
       ylab = 'Squared-Up Rate (%)',
       col = bens_colors[1], pch = 16, cex.main = 0.75
  )
  if(length(args) == 1) {
    legend('bottomright', pnames[1], pch = 16, col = bens_colors[1])
  } else {
    points(d2$launch_angle, d2$squared_up_rate * 100, col = bens_colors[2], pch = 16)
    legend('bottomright', pnames, pch = 16, col = c(bens_colors[1], bens_colors[2]))
  }
  grid(ny = 0)
}

playerNames <- names(alldat)

ui <- fluidPage(
    titlePanel("Ben Clemens' Squared Up Meal"),
    sidebarLayout(
        sidebarPanel(
          selectInput('opt1', NULL, playerNames, 'Aaron Judge'),
          selectInput('opt2', NULL, playerNames, 'Bryce Harper')
        ),
        mainPanel(
           plotOutput("myplot")
        )
    )
)

server <- function(input, output) {
    output$myplot <- renderPlot({
      get_plot(input$opt1, input$opt2)
    })
}

shinyApp(ui = ui, server = server)
