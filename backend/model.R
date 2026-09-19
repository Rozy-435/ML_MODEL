#!/usr/bin/env Rscript

suppressPackageStartupMessages({
	library(jsonlite)
	library(randomForest)
})

args <- commandArgs(trailingOnly = TRUE)
data_path <- if (length(args) > 0) args[[1]] else file.path("data", "crop_weather.csv")
input <- fromJSON(paste(readLines(file("stdin"), warn = FALSE), collapse = ""))

dataset <- read.csv(data_path, stringsAsFactors = FALSE)
dataset$Soil_Type <- factor(dataset$Soil_Type)
dataset$Crop <- factor(dataset$Crop)

model <- randomForest(
	Crop ~ Temperature + Rainfall + Humidity + Soil_Type,
	data = dataset,
	ntree = 300,
	importance = TRUE,
	na.action = na.omit
)

soil_type <- as.character(input$Soil_Type)
if (!soil_type %in% levels(dataset$Soil_Type)) {
	stop(sprintf("Unknown soil type: %s", soil_type))
}

features <- data.frame(
	Temperature = as.numeric(input$Temperature),
	Rainfall = as.numeric(input$Rainfall),
	Humidity = as.numeric(input$Humidity),
	Soil_Type = factor(soil_type, levels = levels(dataset$Soil_Type))
)

probabilities <- predict(model, features, type = "prob")[1, ]
probabilities <- sort(probabilities, decreasing = TRUE)
top_crop <- names(probabilities)[[1]]

result <- list(
	crop = top_crop,
	confidence = round(as.numeric(probabilities[[1]]) * 100, 1),
	alternatives = lapply(seq_len(min(3, length(probabilities) - 1)) + 1, function(index) {
		list(
			crop = names(probabilities)[[index]],
			confidence = round(as.numeric(probabilities[[index]]) * 100, 1)
		)
	})
)

cat(toJSON(result, auto_unbox = TRUE))